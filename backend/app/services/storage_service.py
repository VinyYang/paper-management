from sqlalchemy.orm import Session
from typing import Optional
import logging
import os
from pathlib import Path
from datetime import datetime

from ..models import User
from ..config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
    
    def get_user_storage_info(self, db: Session, user_id: int) -> dict:
        """获取用户存储信息"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("用户不存在")
            
            # 计算已用空间
            user_dir = self.upload_dir / str(user_id)
            storage_used = 0
            
            if user_dir.exists():
                for file_path in user_dir.glob("**/*"):
                    if file_path.is_file():
                        storage_used += file_path.stat().st_size
            
            # 更新用户的存储使用量
            user.storage_used = storage_used
            db.commit()
            
            return {
                "storage_capacity": user.storage_capacity,
                "storage_used": storage_used,
                "storage_free": max(0, user.storage_capacity - storage_used),
                "usage_percentage": (storage_used / user.storage_capacity * 100) if user.storage_capacity > 0 else 0
            }
        except Exception as e:
            logger.error(f"获取存储信息失败: {e}")
            raise
    
    def check_storage_space(self, db: Session, user_id: int, file_size: int) -> bool:
        """检查用户是否有足够的存储空间"""
        try:
            storage_info = self.get_user_storage_info(db, user_id)
            return storage_info["storage_free"] >= file_size
        except Exception as e:
            logger.error(f"检查存储空间失败: {e}")
            raise
    
    def update_storage_usage(self, db: Session, user_id: int, file_size: int, is_add: bool = True) -> bool:
        """更新用户存储使用量"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("用户不存在")
            
            if is_add:
                user.storage_used += file_size
            else:
                user.storage_used = max(0, user.storage_used - file_size)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"更新存储使用量失败: {e}")
            raise
    
    def get_file_path(self, user_id: int, filename: str) -> Path:
        """获取文件完整路径"""
        return self.upload_dir / str(user_id) / filename
    
    def ensure_user_directory(self, user_id: int) -> Path:
        """确保用户目录存在"""
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(exist_ok=True)
        return user_dir 