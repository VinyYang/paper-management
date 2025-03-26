from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..models.user_interest import UserInterest
from ..schemas.user_interest import UserInterestCreate, UserInterestUpdate

logger = logging.getLogger(__name__)

def get_user_interest(db: Session, interest_id: int) -> Optional[UserInterest]:
    """获取用户兴趣"""
    try:
        return db.query(UserInterest).filter(UserInterest.id == interest_id).first()
    except Exception as e:
        logger.error(f"获取用户兴趣失败: {str(e)}")
        return None

def get_user_interests(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[UserInterest]:
    """获取用户兴趣列表"""
    try:
        query = db.query(UserInterest)
        if user_id is not None:
            query = query.filter(UserInterest.user_id == user_id)
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"获取用户兴趣列表失败: {str(e)}")
        return []

def create_user_interest(
    db: Session, 
    interest: UserInterestCreate,
    user_id: int
) -> Optional[UserInterest]:
    """创建用户兴趣"""
    try:
        db_interest = UserInterest(
            **interest.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_interest)
        db.commit()
        db.refresh(db_interest)
        return db_interest
    except Exception as e:
        logger.error(f"创建用户兴趣失败: {str(e)}")
        db.rollback()
        return None

def update_user_interest(
    db: Session, 
    interest_id: int,
    interest: UserInterestUpdate
) -> Optional[UserInterest]:
    """更新用户兴趣"""
    try:
        db_interest = db.query(UserInterest).filter(UserInterest.id == interest_id).first()
        if not db_interest:
            return None
            
        update_data = interest.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_interest, field, value)
            
        db.commit()
        db.refresh(db_interest)
        return db_interest
    except Exception as e:
        logger.error(f"更新用户兴趣失败: {str(e)}")
        db.rollback()
        return None

def delete_user_interest(db: Session, interest_id: int) -> bool:
    """删除用户兴趣"""
    try:
        db_interest = db.query(UserInterest).filter(UserInterest.id == interest_id).first()
        if not db_interest:
            return False
            
        db.delete(db_interest)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"删除用户兴趣失败: {str(e)}")
        db.rollback()
        return False

def get_user_interests_by_user(
    db: Session, 
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[UserInterest]:
    """获取用户的所有兴趣"""
    try:
        return db.query(UserInterest)\
            .filter(UserInterest.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    except Exception as e:
        logger.error(f"获取用户兴趣列表失败: {str(e)}")
        return []

def update_interest_weight(
    db: Session,
    interest_id: int,
    weight: float
) -> Optional[UserInterest]:
    """更新兴趣权重"""
    try:
        db_interest = db.query(UserInterest).filter(UserInterest.id == interest_id).first()
        if not db_interest:
            return None
            
        db_interest.weight = weight
        db_interest.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_interest)
        return db_interest
    except Exception as e:
        logger.error(f"更新兴趣权重失败: {str(e)}")
        db.rollback()
        return None

def clear_user_interests(db: Session, user_id: int) -> bool:
    """清除用户的所有兴趣"""
    try:
        db.query(UserInterest).filter(UserInterest.user_id == user_id).delete()
        db.commit()
        return True
    except Exception as e:
        logger.error(f"清除用户兴趣失败: {str(e)}")
        db.rollback()
        return False 