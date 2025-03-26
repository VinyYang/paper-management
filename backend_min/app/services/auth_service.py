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

# 使用配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# 创建密码上下文，配置增强兼容性
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
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

def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
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

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 添加日志
        logger.debug("开始验证令牌")
        
        # 解码JWT令牌
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                logger.warning("令牌中没有用户名字段")
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError as e:
            logger.error(f"JWT令牌解码失败: {str(e)}")
            raise credentials_exception
        
        # 使用传统的查询语法查找用户
        user = db.query(User).filter(User.username == token_data.username).first()
        
        if user is None:
            logger.warning(f"用户名 '{token_data.username}' 不存在")
            raise credentials_exception
        
        # 检查用户是否被禁用
        try:
            check_user_active(user)
        except HTTPException as e:
            logger.warning(f"用户 '{token_data.username}' 被禁用")
            raise e
        
        logger.debug(f"用户 '{user.username}' 验证成功")
        return user
    except Exception as e:
        # 捕获所有其他异常
        logger.error(f"验证用户时发生未预期错误: {str(e)}")
        raise credentials_exception

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user:
        raise HTTPException(status_code=400, detail="用户不存在")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user 