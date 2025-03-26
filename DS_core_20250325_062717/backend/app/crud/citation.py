from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..models import Citation, Paper
from ..schemas.citation import CitationCreate, CitationUpdate

# 设置日志
logger = logging.getLogger(__name__)

def get_citation(db: Session, citation_id: int) -> Optional[Citation]:
    """根据ID获取引用"""
    return db.query(Citation).filter(Citation.id == citation_id).first()

def get_citations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    paper_id: Optional[int] = None
) -> List[Citation]:
    """获取引用列表"""
    query = db.query(Citation)
    if paper_id:
        query = query.filter(Citation.paper_id == paper_id)
    return query.offset(skip).limit(limit).all()

def create_citation(db: Session, citation: CitationCreate) -> Citation:
    """创建新引用"""
    try:
        db_citation = Citation(
            **citation.model_dump(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_citation)
        db.commit()
        db.refresh(db_citation)
        return db_citation
    except Exception as e:
        logger.error(f"创建引用失败: {str(e)}")
        db.rollback()
        raise

def update_citation(db: Session, citation_id: int, citation: CitationUpdate) -> Optional[Citation]:
    """更新引用信息"""
    try:
        db_citation = get_citation(db, citation_id)
        if not db_citation:
            return None
            
        update_data = citation.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_citation, field, value)
            
        db_citation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_citation)
        return db_citation
    except Exception as e:
        logger.error(f"更新引用失败: {str(e)}")
        db.rollback()
        raise

def delete_citation(db: Session, citation_id: int) -> bool:
    """删除引用"""
    try:
        db_citation = get_citation(db, citation_id)
        if not db_citation:
            return False
            
        db.delete(db_citation)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"删除引用失败: {str(e)}")
        db.rollback()
        raise

def get_citations_by_paper(db: Session, paper_id: int, skip: int = 0, limit: int = 100) -> List[Citation]:
    """获取特定论文的所有引用"""
    return db.query(Citation).filter(Citation.paper_id == paper_id).offset(skip).limit(limit).all() 