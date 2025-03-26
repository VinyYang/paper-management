from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import timedelta, datetime
import os
import shutil
import logging
import traceback
from fastapi.responses import FileResponse

from ..dependencies import get_db, get_current_user, get_current_admin, create_access_token, create_guest_user
from ..models import User, UserRole, UserActivity, Paper
from ..schemas.user import (
    UserCreate,
    UserUpdate,
    User as UserSchema,
    UserWithPapers,
    UserProfile
)
from ..schemas.token import Token
from ..config import settings
from ..crud.user import create_user, get_user_by_username
from ..services.file_service import FileService
from ..services.auth_service import AuthService
from ..schemas.paper import Paper as PaperSchema
from ..utils import logger

# 创建路由器
router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# 初始化文件服务
file_service = FileService(upload_dir=settings.UPLOAD_DIRECTORY if hasattr(settings, "UPLOAD_DIRECTORY") else "uploads")
auth_service = AuthService()

@router.post("/register", response_model=UserSchema)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """注册新用户"""
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    db_user = create_user(db, user_data)
    
    return UserSchema.from_orm(db_user)

@router.get("/guest", response_model=Token)
@router.post("/guest", response_model=Token)
async def login_as_guest(db: Session = Depends(get_db)):
    """创建一个临时游客账户并返回访问令牌"""
    try:
        token_data = await create_guest_user(db)
        return token_data
    except Exception as e:
        logger.error(f"创建游客账户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建游客账户失败，请稍后再试"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录获取访问令牌"""
    user = get_user_by_username(db, form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的详细信息"""
    try:
        # 检查并处理可能缺失的属性
        user_fields = {
            'first_name': '',
            'last_name': '',
            'avatar_url': None,
            'fullname': '',
            'bio': '',
            'is_active': True
        }
        
        for field, default_value in user_fields.items():
            if not hasattr(current_user, field) or getattr(current_user, field) is None:
                setattr(current_user, field, default_value)
            
        return UserSchema.from_orm(current_user)
    except Exception as e:
        logger.error(f"读取当前用户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

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
            current_user.hashed_password = auth_service.get_password_hash(value)
        elif key != "password":
            setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserSchema.from_orm(current_user)

@router.get("/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # 只有管理员可以获取所有用户列表
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserSchema.from_orm(user) for user in users]

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
        raise HTTPException(status_code=404, detail="用户不存在")
    
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"删除用户失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除用户失败")

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

@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（仅管理员）"""
    try:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        
        users = db.query(User).offset(skip).limit(limit).all()
        return [UserSchema.from_orm(user) for user in users]
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户详情"""
    try:
        # 检查权限
        if current_user.id != user_id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限访问此用户信息"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserSchema.from_orm(user)
    except Exception as e:
        logger.error(f"获取用户详情失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取用户详情失败: {str(e)}")

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    try:
        # 检查权限
        if current_user.id != user_id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限更新此用户信息"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新字段
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return UserSchema.from_orm(user)
    except Exception as e:
        db.rollback()
        logger.error(f"更新用户信息失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用户（仅管理员）"""
    try:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 不允许删除管理员用户
        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除管理员用户"
            )
        
        db.delete(user)
        db.commit()
        
        return {"message": "用户已成功删除"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除用户失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

@router.put("/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """激活/禁用用户（仅管理员）"""
    try:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 切换用户状态
        user.is_active = not user.is_active
        db.commit()
        
        status_text = "激活" if user.is_active else "禁用"
        return {"message": f"用户已成功{status_text}"}
    except Exception as e:
        db.rollback()
        logger.error(f"更新用户状态失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"更新用户状态失败: {str(e)}")

@router.get("/me/papers", response_model=List[PaperSchema])
@router.get("/papers", response_model=List[PaperSchema])
async def get_user_papers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有论文"""
    try:
        # 添加详细的调试日志
        logger.info(f"开始获取用户论文，用户ID: {current_user.id}, 跳过: {skip}, 限制: {limit}")
        
        # 检查用户是否存在论文
        papers_count = db.query(Paper).filter(Paper.user_id == current_user.id).count()
        logger.info(f"用户论文总数: {papers_count}")
        
        # 获取论文列表
        papers = db.query(Paper).filter(Paper.user_id == current_user.id).offset(skip).limit(limit).all()
        logger.info(f"成功检索到论文数量: {len(papers)}")
        
        # 返回论文列表
        return papers
    except Exception as e:
        logger.error(f"获取用户论文失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"获取用户论文失败: {str(e)}") 