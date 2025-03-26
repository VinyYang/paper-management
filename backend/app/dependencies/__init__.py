from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging
import uuid

from ..config import settings
from ..database import SessionLocal
from ..models.user import User, UserRole
from ..crud.user import get_user_by_username, create_user
from ..services.auth_service import AuthService
from ..schemas.user import UserCreate

# 配置日志
logger = logging.getLogger(__name__)

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 数据库会话依赖
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 认证服务依赖
def get_auth_service():
    """获取认证服务实例"""
    return AuthService()

# 当前用户依赖
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return user

# 管理员用户依赖
async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 创建游客用户
async def create_guest_user(db: Session) -> dict:
    """创建游客用户并返回访问令牌"""
    try:
        # 生成唯一的游客用户名
        guest_username = f"guest_{uuid.uuid4().hex[:8]}"
        
        # 创建游客用户数据
        guest_data = UserCreate(
            username=guest_username,
            email=f"{guest_username}@example.com",
            password=str(uuid.uuid4()),  # 随机密码
            fullname="游客用户",
            bio="这是一个临时游客账户"
        )
        
        # 创建游客用户
        guest_user = create_user(db, guest_data)
        
        # 设置用户角色为游客
        guest_user.role = UserRole.USER
        guest_user.is_active = True
        db.commit()
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": guest_user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": guest_user.id,
                "username": guest_user.username,
                "role": guest_user.role
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"创建游客用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建游客用户失败: {str(e)}"
        ) 