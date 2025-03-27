from fastapi import APIRouter, Depends, HTTPException, status, Body, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import sqlalchemy.orm
from sqlalchemy import text
import logging
import urllib.parse

from ..dependencies import get_db, get_current_user
from ..models import User, Paper, Tag, UserRole, paper_tag, UserActivity
from ..schemas.paper import (
    PaperCreate, 
    PaperUpdate, 
    Paper as PaperSchema,
    PaperWithTags
)
from ..utils import logger

router = APIRouter(
    prefix="",
    tags=["papers"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=PaperWithTags)
async def create_paper(
    paper_data: PaperCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"开始创建论文，标题: {paper_data.title}")
        
        # 检查DOI是否存在（如果提供了DOI）
        if paper_data.doi:
            existing_paper = db.query(Paper).filter(Paper.doi == paper_data.doi).first()
            if existing_paper:
                logger.warning(f"创建论文失败: DOI已存在: {paper_data.doi}")
                raise HTTPException(
                    status_code=409,
                    detail=f"DOI已存在: {paper_data.doi}"
                )
        
        # 创建基本的Paper对象
        paper = Paper(
            title=paper_data.title,
            authors=paper_data.authors,
            venue=paper_data.journal,  # 使用venue字段存储期刊名称
            journal=paper_data.journal,  # 同时设置journal字段
            doi=paper_data.doi,
            abstract=paper_data.abstract,
            year=paper_data.year,  # 设置year字段
            publication_date=datetime(paper_data.year, 1, 1) if paper_data.year else None,
            citation_count=paper_data.citation_count if paper_data.citation_count else 0,
            user_id=current_user.id,
            is_public=True,
            project_id=paper_data.project_id  # 设置项目ID
        )
        
        logger.info(f"创建论文对象: {paper.title}")
        
        # 保存Paper
        db.add(paper)
        db.commit()
        db.refresh(paper)
        logger.info(f"论文保存成功，ID: {paper.id}")
        
        # 如果指定了项目，也建立项目与论文的多对多关联
        if paper_data.project_id is not None:
            try:
                # 添加到project_paper关联表
                logger.info(f"创建论文-项目关联: 论文ID {paper.id}, 项目ID {paper_data.project_id}")
                db.execute(
                    text("INSERT INTO project_paper (project_id, paper_id) VALUES (:project_id, :paper_id)"),
                    {"project_id": paper_data.project_id, "paper_id": paper.id}
                )
                db.commit()
                logger.info(f"论文已添加到项目 {paper_data.project_id}")
            except Exception as e:
                logger.error(f"添加论文到项目失败: {str(e)}")
                # 失败不影响论文创建成功
        
        # 处理标签（如果有的话）
        tags = []
        if paper_data.tags and len(paper_data.tags) > 0:
            try:
                logger.info(f"开始处理标签: {paper_data.tags}")
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
    search: Optional[str] = None,
    year: Optional[int] = None,
    tags: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有论文"""
    try:
        logger.info("开始获取论文列表")
        query = db.query(Paper).filter(Paper.user_id == current_user.id)
        
        # 添加搜索过滤
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Paper.title.ilike(search_term)) | 
                (Paper.abstract.ilike(search_term)) |
                (Paper.authors.ilike(search_term))
            )
        
        # 按年份过滤
        if year:
            query = query.filter(Paper.year == year)
            
        # 按标签过滤
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag in tag_list:
                query = query.filter(Paper.tags.any(name=tag))
        
        # 添加排序
        if sort_by:
            sort_column = getattr(Paper, sort_by, None)
            if sort_column:
                if sort_order.lower() == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                # 默认按创建时间倒序排列
                query = query.order_by(Paper.created_at.desc())
        else:
            # 默认按创建时间倒序排列
            query = query.order_by(Paper.created_at.desc())
            
        logger.info(f"执行查询: 跳过 {skip}, 限制 {limit}")
        papers = query.offset(skip).limit(limit).all()
        logger.info(f"查询结果: {len(papers)} 条论文")
        
        # 为每篇论文构建返回结果
        result = []
        for paper in papers:
            paper_with_tags = PaperWithTags.from_orm(paper)
            paper_with_tags.tags = [tag.name for tag in paper.tags]
            result.append(paper_with_tags)
            
        return result
    except Exception as e:
        logger.error(f"获取论文列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取论文列表失败: {str(e)}")

@router.get("/search", response_model=PaperWithTags)
async def search_paper_by_doi(
    doi: str = Query(..., description="论文的DOI"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据DOI搜索论文
    """
    # URL解码DOI
    decoded_doi = urllib.parse.unquote(doi)
    
    paper = db.query(Paper).filter(
        Paper.doi == decoded_doi,
        Paper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到匹配的论文"
        )
    
    return paper

@router.get("/{paper_id}", response_model=PaperWithTags)
async def get_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个论文详情"""
    try:
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
    except Exception as e:
        logger.error(f"获取论文详情失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取论文详情失败: {str(e)}")

@router.put("/{paper_id}", response_model=PaperSchema)
async def update_paper(
    paper_id: int,
    paper_data: PaperUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新论文信息"""
    try:
        # 获取论文
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
        
        # 处理项目关联的变更
        old_project_id = paper.project_id
        new_project_id = paper_data.project_id
        
        # 记录项目ID变更
        if old_project_id != new_project_id:
            logger.info(f"论文 {paper_id} 的项目关联变更: 从 {old_project_id} 到 {new_project_id}")
        
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
        
        # 确保项目ID被正确设置
        paper.project_id = new_project_id
        
        # 提交更改
        db.commit()
        db.refresh(paper)
        
        # 再次验证项目关联是否正确保存
        updated_paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if updated_paper.project_id != new_project_id:
            logger.warning(f"项目关联未正确保存，尝试再次更新。期望值: {new_project_id}, 实际值: {updated_paper.project_id}")
            # 尝试直接执行SQL更新
            db.execute(
                text("UPDATE papers SET project_id = :project_id WHERE id = :paper_id"),
                {"project_id": new_project_id, "paper_id": paper_id}
            )
            db.commit()
        
        # 记录活动
        if old_project_id != new_project_id:
            activity_metadata = f"{{\"paper_id\": {paper_id}, \"old_project\": {old_project_id}, \"new_project\": {new_project_id}}}"
            activity = UserActivity(
                user_id=current_user.id,
                activity_type="paper_project_changed",
                content=f"论文 '{paper.title}' 的项目关联从 {old_project_id or 'None'} 更改为 {new_project_id or 'None'}",
                activity_metadata=activity_metadata,
                created_at=datetime.utcnow()
            )
            db.add(activity)
            db.commit()
            
            # 确保项目与论文的双向关联更新
            # 如果有新项目，添加论文到该项目
            if new_project_id is not None:
                try:
                    # 检查论文是否已在项目中
                    project_paper_exists = db.execute(
                        text("SELECT 1 FROM project_paper WHERE project_id = :project_id AND paper_id = :paper_id"),
                        {"project_id": new_project_id, "paper_id": paper_id}
                    ).fetchone()
                    
                    if not project_paper_exists:
                        # 添加到project_paper关联表
                        db.execute(
                            text("INSERT INTO project_paper (project_id, paper_id) VALUES (:project_id, :paper_id)"),
                            {"project_id": new_project_id, "paper_id": paper_id}
                        )
                        db.commit()
                        logger.info(f"论文 {paper_id} 已添加到项目 {new_project_id} 的关联表")
                except Exception as e:
                    logger.error(f"更新项目论文关联失败: {str(e)}")
            
            # 如果移除了旧项目，从旧项目中删除论文
            if old_project_id is not None and old_project_id != new_project_id:
                try:
                    db.execute(
                        text("DELETE FROM project_paper WHERE project_id = :project_id AND paper_id = :paper_id"),
                        {"project_id": old_project_id, "paper_id": paper_id}
                    )
                    db.commit()
                    logger.info(f"论文 {paper_id} 已从项目 {old_project_id} 的关联表中移除")
                except Exception as e:
                    logger.error(f"移除旧项目论文关联失败: {str(e)}")
                    
        return paper
    except Exception as e:
        db.rollback()
        logger.error(f"更新论文失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"更新论文失败: {str(e)}")

@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除论文"""
    try:
        # 查找论文
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="论文不存在")
        
        # 检查权限
        if paper.user_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="没有权限删除此论文")
        
        # 删除论文
        db.delete(paper)
        db.commit()
        
        return {"detail": "论文已成功删除"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除论文失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除论文失败: {str(e)}") 