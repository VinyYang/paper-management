from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..models import Paper, User, Concept, Citation
from ..schemas.paper import PaperCreate, PaperUpdate

# 设置日志
logger = logging.getLogger(__name__)

def get_paper(db: Session, paper_id: int) -> Optional[Paper]:
    """根据ID获取论文"""
    return db.query(Paper).filter(Paper.id == paper_id).first()

def get_papers(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[Paper]:
    """获取论文列表"""
    query = db.query(Paper)
    if user_id:
        query = query.filter(Paper.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_paper(db: Session, paper: PaperCreate, user_id: int) -> Paper:
    """创建新论文"""
    try:
        db_paper = Paper(
            **paper.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)
        return db_paper
    except Exception as e:
        logger.error(f"创建论文失败: {str(e)}")
        db.rollback()
        raise

def update_paper(db: Session, paper_id: int, paper: PaperUpdate) -> Optional[Paper]:
    """更新论文信息"""
    try:
        db_paper = get_paper(db, paper_id)
        if not db_paper:
            return None
            
        update_data = paper.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_paper, field, value)
            
        db_paper.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_paper)
        return db_paper
    except Exception as e:
        logger.error(f"更新论文失败: {str(e)}")
        db.rollback()
        raise

def delete_paper(db: Session, paper_id: int) -> bool:
    """删除论文"""
    try:
        db_paper = get_paper(db, paper_id)
        if not db_paper:
            return False
            
        db.delete(db_paper)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"删除论文失败: {str(e)}")
        db.rollback()
        raise

def get_papers_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Paper]:
    """获取用户的所有论文"""
    return db.query(Paper).filter(Paper.user_id == user_id).offset(skip).limit(limit).all()

def get_papers_by_concept(db: Session, concept_id: int, skip: int = 0, limit: int = 100) -> List[Paper]:
    """获取与特定概念相关的论文"""
    return db.query(Paper).join(Paper.concepts).filter(Concept.id == concept_id).offset(skip).limit(limit).all()

def get_papers_by_citation(db: Session, paper_id: int, skip: int = 0, limit: int = 100) -> List[Paper]:
    """获取引用特定论文的论文列表"""
    return db.query(Paper).join(Citation).filter(Citation.cited_paper_id == paper_id).offset(skip).limit(limit).all() 