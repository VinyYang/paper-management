from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import uuid
import logging
from sqlalchemy import text

from .database import get_db
from .models import User, UserRole
from .config import settings
from .schemas.user import UserCreate
from .services.auth_service import AuthService

logger = logging.getLogger(__name__)

# 创建AuthService实例
auth_service = AuthService()

# 验证令牌
async def get_current_user(
    token: str = Depends(auth_service.oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    return await auth_service.get_current_user(token, db)

# 验证当前活跃用户
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return await auth_service.get_current_active_user(current_user)

# 验证管理员权限
async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    return await auth_service.get_current_admin_user(current_user)

# 创建访问令牌
def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    return auth_service.create_access_token(data, expires_delta)

# 创建游客用户并返回令牌
async def create_guest_user(db: Session) -> dict:
    try:
        from .crud.user import create_user
        
        # 生成唯一的游客用户名和邮箱
        unique_id = str(uuid.uuid4())[:8]
        username = f"guest_{unique_id}"
        email = f"guest_{unique_id}@example.com"
        password = unique_id
        
        # 创建游客用户
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
            role=UserRole.USER,
            fullname=f"游客用户-{unique_id}"
        )
        
        logger.info(f"创建游客用户: {username}")
        user = create_user(db, user_data)
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"创建游客用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"游客登录失败: {str(e)}"
        ) 