from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from ..dependencies import get_db, get_current_user
from ..models import User, Tag, Paper
from ..schemas.tag import TagCreate, TagResponse

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.get("/", response_model=List[TagResponse])
async def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的所有标签"""
    try:
        # 获取用户论文的所有标签
        tags = db.query(Tag).join(Paper.tags).filter(Paper.user_id == current_user.id).distinct().all()
        return tags
    except Exception as e:
        logger.error(f"获取标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取标签失败: {str(e)}")

@router.post("/", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新标签"""
    try:
        # 检查标签是否已存在
        existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing_tag:
            return existing_tag
        
        # 创建新标签
        tag = Tag(name=tag_data.name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        
        return tag
    except Exception as e:
        db.rollback()
        logger.error(f"创建标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建标签失败: {str(e)}")

@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除标签"""
    try:
        # 检查标签是否存在
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="标签不存在")
        
        # 检查标签是否被用户的论文使用
        papers_with_tag = db.query(Paper).join(Paper.tags).filter(
            Paper.user_id == current_user.id,
            Tag.id == tag_id
        ).first()
        
        if papers_with_tag:
            raise HTTPException(
                status_code=400,
                detail="该标签正在被使用，无法删除"
            )
        
        # 删除标签
        db.delete(tag)
        db.commit()
        
        return {"detail": "标签已成功删除"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除标签失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除标签失败: {str(e)}")

@router.get("/papers/{paper_id}", response_model=List[TagResponse])
async def get_paper_tags(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取论文的所有标签"""
    try:
        # 检查论文是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == current_user.id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="论文不存在或无权访问")
        
        # 获取论文的标签
        tags = paper.tags
        return tags
    except Exception as e:
        logger.error(f"获取论文标签失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取论文标签失败: {str(e)}") 