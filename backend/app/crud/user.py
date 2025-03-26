from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging
from ..models import User, UserRole
from ..schemas.user import UserCreate, UserUpdate
from ..services.auth_service import AuthService

# 设置日志
logger = logging.getLogger(__name__)

# 创建AuthService实例
auth_service = AuthService()

def get_user(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()

def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    role: Optional[UserRole] = None
) -> List[User]:
    """获取用户列表"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """创建新用户"""
    try:
        # 检查用户名是否已存在
        if get_user_by_username(db, user.username):
            logger.warning(f"用户名 '{user.username}' 已存在")
            raise ValueError("用户名已存在")
            
        # 检查邮箱是否已存在
        if get_user_by_email(db, user.email):
            logger.warning(f"邮箱 '{user.email}' 已存在")
            raise ValueError("邮箱已存在")
        
        # 创建用户实例
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=auth_service.get_password_hash(user.password),
            role=user.role,
            fullname=user.fullname,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 添加到数据库
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"成功创建用户: {user.username}")
        return db_user
        
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        db.rollback()
        raise

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            logger.warning(f"用户ID {user_id} 不存在")
            return None
            
        # 更新用户信息
        update_data = user.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = auth_service.get_password_hash(update_data.pop("password"))
            
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"成功更新用户: {db_user.username}")
        return db_user
        
    except Exception as e:
        logger.error(f"更新用户失败: {str(e)}")
        db.rollback()
        raise

def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            logger.warning(f"用户ID {user_id} 不存在")
            return False
            
        db.delete(db_user)
        db.commit()
        
        logger.info(f"成功删除用户: {db_user.username}")
        return True
        
    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        db.rollback()
        raise

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户凭据"""
    try:
        user = get_user_by_username(db, username)
        if not user:
            logger.warning(f"用户名 '{username}' 不存在")
            return None
            
        if not auth_service.verify_password(password, user.hashed_password):
            logger.warning(f"用户 '{username}' 密码验证失败")
            return None
            
        logger.info(f"用户 '{username}' 验证成功")
        return user
        
    except Exception as e:
        logger.error(f"验证用户失败: {str(e)}")
        return None 