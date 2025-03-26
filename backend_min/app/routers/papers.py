from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import sqlalchemy.orm
from sqlalchemy import text

from ..dependencies import get_db, get_current_user
from ..models import User, Paper, Tag, UserRole, paper_tag
from ..schemas.paper import (
    PaperCreate, 
    PaperUpdate, 
    Paper as PaperSchema,
    PaperWithTags
)
from ..config import settings
from ..utils import logger

router = APIRouter()

@router.post("/", response_model=PaperWithTags)
async def create_paper(
    paper_data: PaperCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"开始创建论文，标题: {paper_data.title}")
        
        # 检查DOI是否存在（如果提供了DOI）
        existing_paper = None
        if paper_data.doi:
            existing_paper = db.query(Paper).filter(Paper.doi == paper_data.doi).first()
            if existing_paper:
                logger.info(f"DOI已存在: {paper_data.doi}，更新现有记录")
                # 更新现有记录
                existing_paper.title = paper_data.title
                existing_paper.authors = paper_data.authors
                existing_paper.venue = paper_data.journal
                existing_paper.journal = paper_data.journal
                existing_paper.abstract = paper_data.abstract
                existing_paper.year = paper_data.year
                existing_paper.publication_date = datetime(paper_data.year, 1, 1) if paper_data.year else None
                existing_paper.citation_count = paper_data.citations if paper_data.citations else 0
                existing_paper.updated_at = datetime.now()
                
                # 保存更新
                db.commit()
                db.refresh(existing_paper)
                paper = existing_paper
                logger.info(f"现有论文更新成功，ID: {paper.id}")
        
        # 如果不存在，则创建新记录
        if not existing_paper:
            # 先创建基本的Paper对象，不包含任何关系
            paper = Paper(
                title=paper_data.title,
                authors=paper_data.authors,
                venue=paper_data.journal,  # 使用venue字段存储期刊名称
                journal=paper_data.journal,  # 同时设置journal字段
                doi=paper_data.doi,
                abstract=paper_data.abstract,
                year=paper_data.year,  # 设置year字段
                publication_date=datetime(paper_data.year, 1, 1) if paper_data.year else None,
                citation_count=paper_data.citations if paper_data.citations else 0,
                user_id=current_user.id,
                is_public=True
            )
            
            logger.info(f"创建论文对象: {paper.title}")
            
            # 先保存Paper
            db.add(paper)
            db.commit()
            db.refresh(paper)
            logger.info(f"论文保存成功，ID: {paper.id}")
        
        # 处理标签（如果有的话）
        tags = []
        if paper_data.tags and len(paper_data.tags) > 0:
            try:
                logger.info(f"开始处理标签: {paper_data.tags}")
                
                # 如果是更新现有论文，先清除所有现有标签关联
                if existing_paper:
                    db.execute(
                        text("DELETE FROM paper_tag WHERE paper_id = :paper_id"),
                        {"paper_id": paper.id}
                    )
                    db.commit()
                
                for tag_name in paper_data.tags:
                    # 查找或创建标签
                    tag = db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        logger.info(f"创建新标签: {tag_name}")
                        tag = Tag(name=tag_name)
                        db.add(tag)
                        db.commit()
                        db.refresh(tag)
                    else:
                        logger.info(f"使用已有标签: {tag_name}, ID: {tag.id}")
                    
                    # 使用原始SQL直接添加关联
                    logger.info(f"添加论文-标签关联: 论文ID {paper.id}, 标签ID {tag.id}")
                    
                    # 检查关联是否已存在
                    existing = db.execute(
                        text("SELECT 1 FROM paper_tag WHERE paper_id = :paper_id AND tag_id = :tag_id"),
                        {"paper_id": paper.id, "tag_id": tag.id}
                    ).fetchone()
                    
                    if not existing:
                        db.execute(
                            text("INSERT INTO paper_tag (paper_id, tag_id) VALUES (:paper_id, :tag_id)"),
                            {"paper_id": paper.id, "tag_id": tag.id}
                        )
                        db.commit()
                    
                    tags.append(tag_name)
                logger.info("标签处理完成")
            except Exception as tag_error:
                logger.error(f"添加标签时出错: {str(tag_error)}")
                logger.exception("标签错误详情")
                # 标签添加失败不影响论文创建成功
        
        # 创建带有标签信息的返回对象
        paper_with_tags = {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "journal": paper.journal,
            "doi": paper.doi,
            "abstract": paper.abstract,
            "year": paper.year,
            "citations": paper.citation_count,
            "user_id": paper.user_id,
            "created_at": paper.created_at,
            "updated_at": paper.updated_at,
            "tags": tags
        }
        
        logger.info("论文创建完成")
        return paper_with_tags
    except Exception as e:
        db.rollback()
        logger.error(f"创建论文失败: {str(e)}")
        logger.exception("详细错误信息")
        raise HTTPException(status_code=500, detail=f"创建论文失败: {str(e)}")

@router.get("/", response_model=List[PaperWithTags])
async def get_papers(
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 构建查询
    query = db.query(Paper).filter(Paper.user_id == current_user.id)
    
    # 应用过滤条件
    if title:
        query = query.filter(Paper.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Paper.authors.ilike(f"%{author}%"))
    if year:
        query = query.filter(Paper.year == year)
    if tag:
        query = query.join(Paper.tags).filter(Tag.name == tag)
    
    # 执行查询
    papers = query.offset(skip).limit(limit).all()
    return papers

@router.get("/{paper_id}", response_model=PaperWithTags)
async def get_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文不存在或无权访问"
        )
    
    return paper

@router.put("/{paper_id}", response_model=PaperSchema)
async def update_paper(
    paper_id: int,
    paper_data: PaperUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文不存在或无权访问"
        )
    
    # 检查DOI是否已被其他论文使用
    if paper_data.doi and paper_data.doi != paper.doi:
        existing_paper = db.query(Paper).filter(
            Paper.doi == paper_data.doi, 
            Paper.id != paper_id
        ).first()
        if existing_paper:
            raise HTTPException(
                status_code=409,
                detail=f"DOI已存在: {paper_data.doi}"
            )
    
    # 更新字段
    for key, value in paper_data.dict(exclude_unset=True).items():
        if key == "tags":
            # 处理标签
            if value:
                # 清除现有标签
                paper.tags = []
                
                # 添加新标签
                for tag_name in value:
                    tag = db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.add(tag)
                        db.commit()
                        db.refresh(tag)
                    
                    paper.tags.append(tag)
        else:
            # 更新其他字段
            setattr(paper, key, value)
    
    db.commit()
    db.refresh(paper)
    return paper

@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除论文"""
    try:
        # 1. 首先简单查询paper_id是否存在
        paper_exists = db.query(Paper.id, Paper.user_id).filter(Paper.id == paper_id).first()
        if not paper_exists:
            raise HTTPException(status_code=404, detail="论文不存在")
        
        # 2. 检查权限
        if paper_exists.user_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="没有权限删除此论文")
        
        # 3. 使用事务来确保所有操作要么全部成功，要么全部失败
        with db.begin_nested():
            # 尝试删除关联表数据，使用try-except捕获可能的错误
            try:
                db.execute(text("DELETE FROM paper_concepts WHERE paper_id = :paper_id"), {"paper_id": paper_id})
            except Exception as e:
                logger.warning(f"删除paper_concepts关联时出错: {str(e)}")
            
            try:
                db.execute(text("DELETE FROM paper_tags WHERE paper_id = :paper_id"), {"paper_id": paper_id})
            except Exception as e:
                logger.warning(f"删除paper_tags关联时出错: {str(e)}")
            
            try:
                db.execute(text("DELETE FROM project_paper WHERE paper_id = :paper_id"), {"paper_id": paper_id})
            except Exception as e:
                logger.warning(f"删除project_paper关联时出错: {str(e)}")
            
            # 4. 删除论文本身
            db.execute(text("DELETE FROM papers WHERE id = :paper_id"), {"paper_id": paper_id})
        
        # 提交事务
        db.commit()
        
        return {"message": "论文已成功删除"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除论文时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除论文失败: {str(e)}")

@router.get("/search", response_model=PaperWithTags)
async def search_paper_by_doi(
    doi: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据DOI搜索论文
    """
    paper = db.query(Paper).filter(
        Paper.doi == doi,
        Paper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到匹配的论文"
        )
    
    return paper 