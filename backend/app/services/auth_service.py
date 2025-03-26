from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..models import User, UserRole
from ..schemas.user import TokenData
from ..config import settings
from .permission_service import check_user_active

# 设置日志
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        # 使用配置
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = settings.ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

        # 创建密码上下文，配置增强兼容性
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            # 直接使用bcrypt库而不是passlib的verify
            import bcrypt
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"密码验证错误: {str(e)}")
            return False

    def get_password_hash(self, password: str) -> str:
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"密码哈希错误: {str(e)}")
            # 降级方案
            try:
                import bcrypt
                salt = bcrypt.gensalt(rounds=12)
                return bcrypt.hashpw(password.encode(), salt).decode()
            except Exception as e2:
                logger.error(f"备用密码哈希也失败: {str(e2)}")
                raise

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/token")), db: Session = Depends(get_db)) -> User:
        """获取当前用户"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
            
        user = get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        """获取当前活跃用户"""
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="用户未激活")
        return current_user

    async def get_current_admin_user(
        self,
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        return current_user 