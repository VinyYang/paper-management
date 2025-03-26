from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from ..dependencies import get_db, get_current_user
from ..models import User, Project
from ..schemas.project import Project as ProjectSchema, ProjectWithPapers, ProjectCreate, ProjectUpdate
from ..services.project_service import ProjectService

router = APIRouter(
    prefix="",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

# 初始化服务
project_service = ProjectService()

@router.get("/", response_model=List[ProjectSchema])
def read_projects(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有项目"""
    try:
        projects = project_service.get_projects(db, user_id=current_user.id, skip=skip, limit=limit)
        return projects
    except Exception as e:
        logger.error(f"获取项目列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取项目列表失败"
        )

@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新项目"""
    try:
        return project_service.create_project(db, project_data=project, user_id=current_user.id)
    except Exception as e:
        logger.error(f"创建项目失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建项目失败"
        )

@router.get("/{project_id}", response_model=ProjectWithPapers)
def read_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取特定项目详情，包含项目中的论文"""
    try:
        project = project_service.get_project_with_papers(db, project_id=project_id, user_id=current_user.id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目 {project_id} 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取项目详情失败"
        )

@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(
    project_id: int, 
    project: ProjectUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新项目"""
    try:
        updated_project = project_service.update_project(
            db, project_id=project_id, project_data=project, user_id=current_user.id
        )
        if updated_project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新项目 {project_id} 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新项目失败"
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除项目"""
    try:
        success = project_service.delete_project(db, project_id=project_id, user_id=current_user.id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        return {"detail": "项目已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除项目 {project_id} 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除项目失败"
        )

@router.post("/{project_id}/papers/{paper_id}", status_code=status.HTTP_201_CREATED)
def add_paper_to_project(
    project_id: int, 
    paper_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """将论文添加到项目中"""
    try:
        logger.info(f"尝试将论文 {paper_id} 添加到项目 {project_id}")
        project_paper = project_service.add_paper_to_project(
            db, project_id=project_id, paper_id=paper_id, user_id=current_user.id
        )
        if project_paper is None:
            logger.warning(f"项目 {project_id} 或论文 {paper_id} 不存在")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目或论文不存在")
        return {"detail": "论文已添加到项目", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"将论文 {paper_id} 添加到项目 {project_id} 失败: {e}")
        # 返回详细的错误信息，帮助调试
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"将论文添加到项目失败: {str(e)}"
        )

@router.delete("/{project_id}/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_paper_from_project(
    project_id: int, 
    paper_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从项目中移除论文"""
    try:
        success = project_service.remove_paper_from_project(
            db, project_id=project_id, paper_id=paper_id, user_id=current_user.id
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目或论文不存在")
        return {"detail": "论文已从项目中移除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"从项目 {project_id} 移除论文 {paper_id} 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="从项目中移除论文失败"
        ) 