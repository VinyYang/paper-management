from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime

from ..models import User
from ..schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self):
        pass

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """获取特定用户"""
        from ..crud.user import get_user
        return get_user(db, user_id)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        from ..crud.user import get_user_by_email
        return get_user_by_email(db, email)

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        from ..crud.user import get_users
        return get_users(db, skip=skip, limit=limit)

    def create_user(self, db: Session, **kwargs) -> User:
        """创建新用户"""
        from ..crud.user import create_user
        return create_user(db, **kwargs)

    def update_user(self, db: Session, user: User, **kwargs) -> User:
        """更新用户信息"""
        from ..crud.user import update_user
        return update_user(db, user, **kwargs)

    def delete_user(self, db: Session, user_id: int) -> bool:
        """删除用户"""
        from ..crud.user import delete_user
        return delete_user(db, user_id)

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """验证用户"""
        from ..crud.user import authenticate_user
        return authenticate_user(db, email, password)

    def update_user_profile(self, db: Session, user: User, **kwargs) -> User:
        """更新用户个人资料"""
        try:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.now()
            db.commit()
            db.refresh(user)
            return user
        except SQLAlchemyError as e:
            db.rollback()
            raise

    def update_user_password(self, db: Session, user: User, new_password: str) -> User:
        """更新用户密码"""
        try:
            user.hashed_password = new_password
            user.updated_at = datetime.now()
            db.commit()
            db.refresh(user)
            return user
        except SQLAlchemyError as e:
            db.rollback()
            raise 