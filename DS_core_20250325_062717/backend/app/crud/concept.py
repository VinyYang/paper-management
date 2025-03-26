from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..models import Concept, Paper, User
from ..schemas.concept import ConceptCreate, ConceptUpdate

# 设置日志
logger = logging.getLogger(__name__)

def get_concept(db: Session, concept_id: int) -> Optional[Concept]:
    """根据ID获取概念"""
    return db.query(Concept).filter(Concept.id == concept_id).first()

def get_concepts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[Concept]:
    """获取概念列表"""
    query = db.query(Concept)
    if user_id:
        query = query.filter(Concept.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_concept(db: Session, concept: ConceptCreate, user_id: int) -> Concept:
    """创建新概念"""
    try:
        db_concept = Concept(
            **concept.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_concept)
        db.commit()
        db.refresh(db_concept)
        return db_concept
    except Exception as e:
        logger.error(f"创建概念失败: {str(e)}")
        db.rollback()
        raise

def update_concept(db: Session, concept_id: int, concept: ConceptUpdate) -> Optional[Concept]:
    """更新概念信息"""
    try:
        db_concept = get_concept(db, concept_id)
        if not db_concept:
            return None
            
        update_data = concept.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_concept, field, value)
            
        db_concept.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_concept)
        return db_concept
    except Exception as e:
        logger.error(f"更新概念失败: {str(e)}")
        db.rollback()
        raise

def delete_concept(db: Session, concept_id: int) -> bool:
    """删除概念"""
    try:
        db_concept = get_concept(db, concept_id)
        if not db_concept:
            return False
            
        db.delete(db_concept)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"删除概念失败: {str(e)}")
        db.rollback()
        raise

def get_concepts_by_paper(db: Session, paper_id: int, skip: int = 0, limit: int = 100) -> List[Concept]:
    """获取与特定论文相关的概念"""
    return db.query(Concept).join(Concept.papers).filter(Paper.id == paper_id).offset(skip).limit(limit).all()

def get_concepts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Concept]:
    """获取用户的所有概念"""
    return db.query(Concept).filter(Concept.user_id == user_id).offset(skip).limit(limit).all() 