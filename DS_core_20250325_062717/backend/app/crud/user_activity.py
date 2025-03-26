from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..models import UserActivity, User
from ..schemas.user_activity import UserActivityCreate, UserActivityUpdate

# 设置日志
logger = logging.getLogger(__name__)

def get_user_activity(db: Session, activity_id: int) -> Optional[UserActivity]:
    """根据ID获取用户活动"""
    return db.query(UserActivity).filter(UserActivity.id == activity_id).first()

def get_user_activities(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[UserActivity]:
    """获取用户活动列表"""
    query = db.query(UserActivity)
    if user_id:
        query = query.filter(UserActivity.user_id == user_id)
    return query.order_by(UserActivity.created_at.desc()).offset(skip).limit(limit).all()

def create_user_activity(db: Session, activity: UserActivityCreate, user_id: int) -> UserActivity:
    """创建新用户活动"""
    try:
        db_activity = UserActivity(
            **activity.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity
    except Exception as e:
        logger.error(f"创建用户活动失败: {str(e)}")
        db.rollback()
        raise

def update_user_activity(db: Session, activity_id: int, activity: UserActivityUpdate) -> Optional[UserActivity]:
    """更新用户活动信息"""
    try:
        db_activity = get_user_activity(db, activity_id)
        if not db_activity:
            return None
            
        update_data = activity.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_activity, field, value)
            
        db_activity.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_activity)
        return db_activity
    except Exception as e:
        logger.error(f"更新用户活动失败: {str(e)}")
        db.rollback()
        raise

def delete_user_activity(db: Session, activity_id: int) -> bool:
    """删除用户活动"""
    try:
        db_activity = get_user_activity(db, activity_id)
        if not db_activity:
            return False
            
        db.delete(db_activity)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"删除用户活动失败: {str(e)}")
        db.rollback()
        raise

def get_user_activities_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[UserActivity]:
    """获取用户的所有活动"""
    return db.query(UserActivity).filter(UserActivity.user_id == user_id).order_by(UserActivity.created_at.desc()).offset(skip).limit(limit).all()

def get_user_activities_by_type(db: Session, activity_type: str, skip: int = 0, limit: int = 100) -> List[UserActivity]:
    """获取特定类型的所有用户活动"""
    return db.query(UserActivity).filter(UserActivity.activity_type == activity_type).order_by(UserActivity.created_at.desc()).offset(skip).limit(limit).all()

def clear_user_activities(db: Session, user_id: int) -> bool:
    """清除用户的所有活动记录"""
    try:
        db.query(UserActivity).filter(UserActivity.user_id == user_id).delete()
        db.commit()
        return True
    except Exception as e:
        logger.error(f"清除用户活动记录失败: {str(e)}")
        db.rollback()
        raise 