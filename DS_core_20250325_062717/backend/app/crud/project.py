from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime
import logging

from ..models import Project, project_paper, Paper, User
from ..schemas.project import ProjectCreate, ProjectUpdate

# 设置日志
logger = logging.getLogger(__name__)

def get_project(db: Session, project_id: int) -> Optional[Project]:
    """根据ID获取项目"""
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[Project]:
    """获取项目列表"""
    query = db.query(Project)
    if user_id:
        query = query.filter(Project.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_project(db: Session, project: ProjectCreate, user_id: int) -> Project:
    """创建新项目"""
    try:
        db_project = Project(
            **project.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        logger.error(f"创建项目失败: {str(e)}")
        db.rollback()
        raise

def update_project(db: Session, project_id: int, project: ProjectUpdate) -> Optional[Project]:
    """更新项目信息"""
    try:
        db_project = get_project(db, project_id)
        if not db_project:
            return None
            
        update_data = project.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
            
        db_project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        logger.error(f"更新项目失败: {str(e)}")
        db.rollback()
        raise

def delete_project(db: Session, project_id: int) -> bool:
    """删除项目"""
    try:
        db_project = get_project(db, project_id)
        if not db_project:
            return False
            
        db.delete(db_project)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"删除项目失败: {str(e)}")
        db.rollback()
        raise

def get_projects_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
    """获取用户的所有项目"""
    return db.query(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()

def add_paper_to_project(db: Session, project_id: int, paper_id: int) -> Optional[project_paper]:
    """将论文添加到项目中"""
    try:
        # 检查是否已经存在该关联
        existing = db.query(project_paper).filter(
            project_paper.c.project_id == project_id,
            project_paper.c.paper_id == paper_id
        ).first()
        
        if existing:
            return existing
            
        # 创建新的关联
        stmt = project_paper.insert().values(
            project_id=project_id,
            paper_id=paper_id
        )
        db.execute(stmt)
        db.commit()
        
        # 获取新创建的关联
        return db.query(project_paper).filter(
            project_paper.c.project_id == project_id,
            project_paper.c.paper_id == paper_id
        ).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise

def remove_paper_from_project(db: Session, project_id: int, paper_id: int) -> bool:
    """从项目中移除论文"""
    try:
        stmt = project_paper.delete().where(
            project_paper.c.project_id == project_id,
            project_paper.c.paper_id == paper_id
        )
        result = db.execute(stmt)
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        raise 