from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import os
from pathlib import Path

from ..models import Paper, User, Note
from ..schemas.paper import PaperCreate, PaperUpdate
from ..schemas.note import NoteCreate, NoteResponse

logger = logging.getLogger(__name__)

class PaperService:
    def get_papers_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Paper]:
        """获取用户的所有论文"""
        return db.query(Paper).filter(Paper.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_paper(self, db: Session, paper_id: int, user_id: int) -> Optional[Paper]:
        """获取单个论文的详细信息"""
        return db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == user_id).first()
    
    def create_paper(self, db: Session, paper: PaperCreate, user_id: int) -> Paper:
        """创建新论文"""
        try:
            db_paper = Paper(
                title=paper.title,
                authors=paper.authors,
                journal=paper.journal,
                year=paper.year,
                doi=paper.doi,
                abstract=paper.abstract,
                keywords=paper.keywords,
                user_id=user_id,
                has_pdf=False
            )
            db.add(db_paper)
            db.commit()
            db.refresh(db_paper)
            return db_paper
        except Exception as e:
            db.rollback()
            logger.error(f"创建论文失败: {e}")
            raise
    
    def update_paper(self, db: Session, paper_id: int, paper_update: PaperUpdate, user_id: int) -> Optional[Paper]:
        """更新论文信息"""
        try:
            db_paper = self.get_paper(db, paper_id, user_id)
            if not db_paper:
                return None
            
            # 检查是否更新了project_id
            old_project_id = db_paper.project_id
            
            update_data = paper_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_paper, key, value)
            
            # 如果project_id发生变化，则更新project_paper关联表
            if 'project_id' in update_data and old_project_id != db_paper.project_id:
                logger.info(f"论文 {paper_id} 的项目从 {old_project_id} 变更为 {db_paper.project_id}")
                
                # 如果原来有项目，先移除旧关联
                if old_project_id is not None:
                    try:
                        from ..crud.project import remove_paper_from_project
                        remove_paper_from_project(db, project_id=old_project_id, paper_id=paper_id)
                        logger.info(f"已从项目 {old_project_id} 移除论文 {paper_id}")
                    except Exception as e:
                        logger.warning(f"移除论文 {paper_id} 与旧项目 {old_project_id} 的关联失败: {e}")
                
                # 如果新项目不为空，则创建新关联
                if db_paper.project_id is not None:
                    try:
                        from ..crud.project import add_paper_to_project
                        add_paper_to_project(db, project_id=db_paper.project_id, paper_id=paper_id)
                        logger.info(f"已将论文 {paper_id} 添加到项目 {db_paper.project_id}")
                    except Exception as e:
                        logger.warning(f"添加论文 {paper_id} 到新项目 {db_paper.project_id} 失败: {e}")
            
            db.commit()
            db.refresh(db_paper)
            return db_paper
        except Exception as e:
            db.rollback()
            logger.error(f"更新论文失败: {e}")
            raise
    
    def delete_paper(self, db: Session, paper_id: int, user_id: int) -> bool:
        """删除论文"""
        try:
            db_paper = self.get_paper(db, paper_id, user_id)
            if not db_paper:
                return False
            
            # 先删除相关的笔记
            db.query(Note).filter(Note.paper_id == paper_id).delete()
            
            # 删除论文
            db.delete(db_paper)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"删除论文失败: {e}")
            raise
    
    def get_paper_notes(self, db: Session, paper_id: int, user_id: int) -> List[Note]:
        """获取论文的所有笔记"""
        # 先检查论文是否属于用户
        paper = self.get_paper(db, paper_id, user_id)
        if not paper:
            return []
        
        return db.query(Note).filter(Note.paper_id == paper_id).all()
    
    def create_note(self, db: Session, note: NoteCreate, paper_id: int, user_id: int) -> Optional[Note]:
        """为论文创建笔记"""
        try:
            # 先检查论文是否属于用户
            paper = self.get_paper(db, paper_id, user_id)
            if not paper:
                return None
            
            db_note = Note(
                content=note.content,
                page_number=note.page_number,
                paper_id=paper_id,
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