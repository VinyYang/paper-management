from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import List

from backend.config import settings
from backend.database.database import get_db
from backend.database.models import User
from backend.utils.logger import logger

oauth2_scheme = OAuth2PasswordRequestForm(scope="")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """验证当前用户并返回用户对象"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证令牌
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # 从令牌中获取用户名
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # 检查用户是否存在
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
            
        # 确保用户有storage_used和storage_capacity属性
        if not hasattr(user, 'storage_used') or user.storage_used is None:
            user.storage_used = 0
            db.commit()
            
        if not hasattr(user, 'storage_capacity') or user.storage_capacity is None:
            user.storage_capacity = 1024  # 默认1GB
            db.commit()
            
        return user
    except JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"验证用户时出错: {str(e)}")
        raise credentials_exception 