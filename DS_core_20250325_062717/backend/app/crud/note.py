from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..models import Note, Paper, User
from ..schemas.note import NoteCreate, NoteUpdate

# 设置日志
logger = logging.getLogger(__name__)

def get_note(db: Session, note_id: int) -> Optional[Note]:
    """根据ID获取笔记"""
    return db.query(Note).filter(Note.id == note_id).first()

def get_notes(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[Note]:
    """获取笔记列表"""
    query = db.query(Note)
    if user_id:
        query = query.filter(Note.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_note(db: Session, note: NoteCreate, user_id: int) -> Note:
    """创建新笔记"""
    try:
        db_note = Note(
            **note.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
    except Exception as e:
        logger.error(f"创建笔记失败: {str(e)}")
        db.rollback()
        raise

def update_note(db: Session, note_id: int, note: NoteUpdate) -> Optional[Note]:
    """更新笔记信息"""
    try:
        db_note = get_note(db, note_id)
        if not db_note:
            return None
            
        update_data = note.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_note, field, value)
            
        db_note.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_note)
        return db_note
    except Exception as e:
        logger.error(f"更新笔记失败: {str(e)}")
        db.rollback()
        raise

def delete_note(db: Session, note_id: int) -> bool:
    """删除笔记"""
    try:
        db_note = get_note(db, note_id)
        if not db_note:
            return False
            
        db.delete(db_note)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"删除笔记失败: {str(e)}")
        db.rollback()
        raise

def get_notes_by_paper(db: Session, paper_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    """获取与特定论文相关的笔记"""
    return db.query(Note).filter(Note.paper_id == paper_id).offset(skip).limit(limit).all()

def get_notes_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    """获取用户的所有笔记"""
    return db.query(Note).filter(Note.user_id == user_id).offset(skip).limit(limit).all() 