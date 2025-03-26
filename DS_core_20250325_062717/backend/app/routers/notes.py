from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from ..dependencies import get_db, get_current_user
from ..models import User, Paper, Note
from ..schemas.note import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.post("/papers/{paper_id}", response_model=NoteResponse)
async def create_paper_note(
    paper_id: int,
    content: str = Body(...),
    page_number: int = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为论文添加笔记"""
    try:
        # 检查论文是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == current_user.id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="论文不存在或无权访问")
        
        # 创建笔记
        note = Note(
            title=f"第{page_number}页笔记",  # 默认标题
            content=content,
            page_number=page_number,
            user_id=current_user.id,
            paper_id=paper_id
        )
        
        db.add(note)
        db.commit()
        db.refresh(note)
        
        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "page_number": note.page_number,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"添加笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加笔记失败: {str(e)}")

@router.get("/papers/{paper_id}", response_model=List[NoteResponse])
async def get_paper_notes(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取论文的笔记"""
    try:
        # 检查论文是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == current_user.id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="论文不存在或无权访问")
        
        # 获取笔记
        notes = db.query(Note).filter(Note.paper_id == paper_id, Note.user_id == current_user.id).all()
        
        return [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "page_number": note.page_number,
                "created_at": note.created_at,
                "updated_at": note.updated_at
            }
            for note in notes
        ]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"获取笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取笔记失败: {str(e)}")

@router.put("/{note_id}", response_model=NoteResponse)
async def update_paper_note(
    note_id: int,
    content: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新论文笔记"""
    try:
        # 检查笔记是否存在
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == current_user.id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在或无权访问")
        
        # 更新笔记
        note.content = content
        note.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(note)
        
        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "page_number": note.page_number,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"更新笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新笔记失败: {str(e)}")

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除论文笔记"""
    try:
        # 检查笔记是否存在
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == current_user.id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在或无权访问")
        
        # 删除笔记
        db.delete(note)
        db.commit()
        
        return None
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"删除笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除笔记失败: {str(e)}") 