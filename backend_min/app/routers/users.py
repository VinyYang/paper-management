from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta, datetime
import os
import shutil
import logging
import traceback
from fastapi.responses import FileResponse

from ..dependencies import get_db, get_current_user, get_current_admin, create_access_token
from ..models import User, UserRole, UserActivity
from ..schemas.user import (
    UserCreate,
    UserUpdate,
    User as UserSchema,
    UserWithPapers,
    Token,
    UserProfile
)
from ..config import settings
from ..crud.user import create_user, verify_password, authenticate_user, pwd_context
from ..services.file_service import FileService

# 添加日志记录器
logger = logging.getLogger(__name__)

router = APIRouter()
file_service = FileService(upload_dir=settings.UPLOAD_DIRECTORY if hasattr(settings, "UPLOAD_DIRECTORY") else "uploads")

@router.post("/register", response_model=UserSchema)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """注册新用户"""
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已被使用")
    
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 创建新用户
    db_user = create_user(db, user_data)
    
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录并获取访问令牌"""
    logger.info(f"尝试用户登录: {form_data.username}")
    try:
        # 验证用户凭据
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"登录失败: 用户 '{form_data.username}' 凭据无效")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"用户 '{user.username}' 凭据验证成功")
            
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        logger.debug(f"为用户 '{user.username}' 创建访问令牌成功")
        
        # 更新用户最后登录时间
        user.last_login = datetime.utcnow()
        db.commit()
        logger.debug(f"更新用户 '{user.username}' 最后登录时间成功")
        
        # 尝试添加用户活动记录，但不影响登录成功
        try:
            activity = UserActivity(
                user_id=user.id,
                activity_type="login",
                content=f"用户 {user.username} 登录系统",
                activity_metadata=None,
                created_at=datetime.utcnow()
            )
            db.add(activity)
            db.commit()
            logger.debug(f"记录用户 '{user.username}' 登录活动成功")
        except Exception as activity_error:
            # 记录错误但不影响登录过程
            logger.error(f"记录用户活动失败，但登录成功: {str(activity_error)}")
            db.rollback()  # 回滚活动记录的事务
        
        logger.info(f"用户 '{user.username}' 登录成功")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as he:
        # 直接重新抛出HTTP异常
        raise he
    except Exception as e:
        # 记录详细的错误信息
        error_msg = f"登录过程中发生未预期错误: {str(e)}"
        logger.error(error_msg)
        logger.error(f"错误详情: {traceback.format_exc()}")
        # 返回通用错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录处理失败，请联系管理员",
        )

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_data: UserUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 检查用户名和邮箱是否已被使用
    if user_data.username and user_data.username != current_user.username:
        db_user = db.query(User).filter(User.username == user_data.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="用户名已被使用")
    
    if user_data.email and user_data.email != current_user.email:
        db_user = db.query(User).filter(User.email == user_data.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 更新用户信息
    for key, value in user_data.dict(exclude_unset=True).items():
        if key == "password" and value:
            current_user.hashed_password = pwd_context.hash(value)
        elif key != "password":
            setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # 只有管理员可以获取所有用户列表
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # 只有管理员可以删除用户
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录的管理员账户"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    db.delete(user)
    db.commit()
    return 

@router.post("/avatar", response_model=UserSchema)
async def update_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 导入文件服务
        from ..services.file_service import FileService
        file_service = FileService(upload_dir=os.path.abspath(settings.UPLOAD_DIRECTORY))
        
        # 使用文件服务保存头像
        avatar_path = await file_service.save_avatar(avatar, current_user.id)
        print(f"头像已成功保存到: {avatar_path}")
        
        # 更新用户头像路径
        current_user.avatar_url = avatar_path
        db.commit()
        db.refresh(current_user)
        
        return current_user
    except Exception as e:
        print(f"头像上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"头像上传失败: {str(e)}"
        )

@router.get("/avatar/{filename}")
async def get_avatar(filename: str):
    """获取用户头像"""
    avatar_path = os.path.join(settings.UPLOAD_DIRECTORY, "avatars", filename)
    
    if not os.path.exists(avatar_path):
        # 返回默认头像
        default_avatar = os.path.join(settings.UPLOAD_DIRECTORY, "avatars", "default.png")
        if os.path.exists(default_avatar):
            return FileResponse(default_avatar)
        else:
            raise HTTPException(status_code=404, detail="头像不存在")
    
    return FileResponse(avatar_path)

# 新增：获取用户当前头像
@router.get("/me/avatar")
async def get_current_avatar(current_user: User = Depends(get_current_user)):
    """获取当前用户头像"""
    if not current_user.avatar_url or not os.path.exists(current_user.avatar_url):
        # 返回默认头像
        default_avatar = os.path.join(settings.UPLOAD_DIRECTORY, "avatars", "default.png")
        if os.path.exists(default_avatar):
            return FileResponse(default_avatar)
        else:
            raise HTTPException(status_code=404, detail="头像不存在")
    
    return FileResponse(current_user.avatar_url) 