from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from ..models import Note, Paper, User
from ..schemas.note import NoteCreate, NoteUpdate, NoteResponse

logger = logging.getLogger(__name__)

class NoteService:
    def get_notes_by_paper(self, db: Session, paper_id: int, user_id: int) -> List[Note]:
        """获取论文的所有笔记"""
        try:
            # 检查论文是否属于用户
            paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == user_id).first()
            if not paper:
                return []
            
            return db.query(Note).filter(Note.paper_id == paper_id).all()
        except Exception as e:
            logger.error(f"获取论文笔记失败: {e}")
            raise
    
    def get_note(self, db: Session, note_id: int, user_id: int) -> Optional[Note]:
        """获取单个笔记"""
        try:
            return db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
        except Exception as e:
            logger.error(f"获取笔记失败: {e}")
            raise
    
    def create_note(self, db: Session, note: NoteCreate, user_id: int) -> Optional[Note]:
        """创建新笔记"""
        try:
            # 检查论文是否属于用户
            paper = db.query(Paper).filter(Paper.id == note.paper_id, Paper.user_id == user_id).first()
            if not paper:
                return None
            
            db_note = Note(
                title=note.title,
                content=note.content,
                page_number=note.page_number,
                paper_id=note.paper_id,
                user_id=user_id
            )
            db.add(db_note)
            db.commit()
            db.refresh(db_note)
            return db_note
        except Exception as e:
            db.rollback()
            logger.error(f"创建笔记失败: {e}")
            raise
    
    def update_note(self, db: Session, note_id: int, note_update: NoteUpdate, user_id: int) -> Optional[Note]:
        """更新笔记"""
        try:
            db_note = self.get_note(db, note_id, user_id)
            if not db_note:
                return None
            
            update_data = note_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_note, key, value)
            
            db.commit()
            db.refresh(db_note)
            return db_note
        except Exception as e:
            db.rollback()
            logger.error(f"更新笔记失败: {e}")
            raise
    
    def delete_note(self, db: Session, note_id: int, user_id: int) -> bool:
        """删除笔记"""
        try:
            db_note = self.get_note(db, note_id, user_id)
            if not db_note:
                return False
            
            db.delete(db_note)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"删除笔记失败: {e}")
            raise
    
    def get_notes_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
        """获取用户的所有笔记"""
        try:
            return db.query(Note).filter(Note.user_id == user_id).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"获取用户笔记失败: {e}")
            raise 