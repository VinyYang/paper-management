from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..models import SearchHistory, User
from ..schemas.search_history import SearchHistoryCreate, SearchHistoryUpdate

# 设置日志
logger = logging.getLogger(__name__)

def get_search_history(db: Session, history_id: int) -> Optional[SearchHistory]:
    """根据ID获取搜索历史"""
    return db.query(SearchHistory).filter(SearchHistory.id == history_id).first()

def get_search_histories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[SearchHistory]:
    """获取搜索历史列表"""
    query = db.query(SearchHistory)
    if user_id:
        query = query.filter(SearchHistory.user_id == user_id)
    return query.order_by(SearchHistory.created_at.desc()).offset(skip).limit(limit).all()

def create_search_history(db: Session, history: SearchHistoryCreate, user_id: int) -> SearchHistory:
    """创建新搜索历史"""
    try:
        db_history = SearchHistory(
            **history.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history
    except Exception as e:
        logger.error(f"创建搜索历史失败: {str(e)}")
        db.rollback()
        raise

def update_search_history(db: Session, history_id: int, history: SearchHistoryUpdate) -> Optional[SearchHistory]:
    """更新搜索历史信息"""
    try:
        db_history = get_search_history(db, history_id)
        if not db_history:
            return None
            
        update_data = history.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_history, field, value)
            
        db_history.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_history)
        return db_history
    except Exception as e:
        logger.error(f"更新搜索历史失败: {str(e)}")
        db.rollback()
        raise

def delete_search_history(db: Session, history_id: int) -> bool:
    """删除搜索历史"""
    try:
        db_history = get_search_history(db, history_id)
        if not db_history:
            return False
            
        db.delete(db_history)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"删除搜索历史失败: {str(e)}")
        db.rollback()
        raise

def get_search_histories_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[SearchHistory]:
    """获取用户的所有搜索历史"""
    return db.query(SearchHistory).filter(SearchHistory.user_id == user_id).order_by(SearchHistory.created_at.desc()).offset(skip).limit(limit).all()

def clear_user_search_history(db: Session, user_id: int) -> bool:
    """清除用户的所有搜索历史"""
    try:
        db.query(SearchHistory).filter(SearchHistory.user_id == user_id).delete()
        db.commit()
        return True
    except Exception as e:
        logger.error(f"清除用户搜索历史失败: {str(e)}")
        db.rollback()
        raise 