from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import List, Optional, Dict
from datetime import datetime

from ..models import Project, project_paper, Paper, User
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectWithPapers, PaperInProject
from ..crud.project import (
    get_project,
    get_projects,
    create_project,
    update_project,
    delete_project,
    add_paper_to_project,
    remove_paper_from_project
)

logger = logging.getLogger(__name__)

class ProjectService:
    def get_projects(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """获取用户的所有项目"""
        try:
            return get_projects(db, user_id=user_id, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"获取项目列表失败: {e}")
            raise
    
    def get_project(self, db: Session, project_id: int, user_id: int) -> Optional[Project]:
        """获取特定项目"""
        try:
            project = get_project(db, project_id=project_id)
            # 检查项目是否属于当前用户
            if not project or project.user_id != user_id:
                return None
            return project
        except Exception as e:
            logger.error(f"获取项目 {project_id} 失败: {e}")
            raise
    
    def create_project(self, db: Session, project_data: ProjectCreate, user_id: int) -> Project:
        """创建新项目"""
        try:
            project_dict = project_data.model_dump()
            return create_project(db, project=project_data, user_id=user_id)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"创建项目失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            raise
    
    def update_project(self, db: Session, project_id: int, project_data: ProjectUpdate, user_id: int) -> Optional[Project]:
        """更新项目"""
        try:
            # 先检查项目是否存在并属于当前用户
            project = self.get_project(db, project_id, user_id)
            if not project:
                return None
            
            # 更新项目
            update_data = project_data.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.now()
            return update_project(db, project=project, **update_data)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"更新项目 {project_id} 失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新项目 {project_id} 失败: {e}")
            raise
    
    def delete_project(self, db: Session, project_id: int, user_id: int) -> bool:
        """删除项目"""
        try:
            # 先检查项目是否存在并属于当前用户
            project = self.get_project(db, project_id, user_id)
            if not project:
                return False
            
            # 删除项目
            return delete_project(db, project_id=project_id)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"删除项目 {project_id} 失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除项目 {project_id} 失败: {e}")
            raise
    
    def add_paper_to_project(self, db: Session, project_id: int, paper_id: int, user_id: int) -> Optional[project_paper]:
        """将论文添加到项目中"""
        try:
            # 先检查项目是否存在并属于当前用户
            project = self.get_project(db, project_id, user_id)
            if not project:
                return None
            
            # 添加论文到项目
            return add_paper_to_project(db, project_id=project_id, paper_id=paper_id)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"将论文 {paper_id} 添加到项目 {project_id} 失败: {e}")
            raise
        except Exception as e:
            logger.error(f"将论文 {paper_id} 添加到项目 {project_id} 失败: {e}")
            raise
    
    def remove_paper_from_project(self, db: Session, project_id: int, paper_id: int, user_id: int) -> bool:
        """从项目中移除论文"""
        try:
            # 先检查项目是否存在并属于当前用户
            project = self.get_project(db, project_id, user_id)
            if not project:
                return False
            
            # 从项目中移除论文
            return remove_paper_from_project(db, project_id=project_id, paper_id=paper_id)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"从项目 {project_id} 移除论文 {paper_id} 失败: {e}")
            raise
        except Exception as e:
            logger.error(f"从项目 {project_id} 移除论文 {paper_id} 失败: {e}")
            raise
    
    def get_project_with_papers(self, db: Session, project_id: int, user_id: int) -> Optional[Dict]:
        """获取特定项目及其关联的论文"""
        try:
            # 首先获取项目信息
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            
            if not project:
                return None
            
            # 获取项目关联的论文
            papers = db.query(Paper).join(
                project_paper,
                Paper.id == project_paper.c.paper_id
            ).filter(
                project_paper.c.project_id == project_id
            ).all()
            
            # 创建带有论文列表的项目信息
            result = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "user_id": project.user_id,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "is_public": project.is_public,
                "papers": []
            }
            
            # 添加论文信息
            for paper in papers:
                paper_data = {
                    "id": paper.id,
                    "title": paper.title,
                    "authors": paper.authors,
                    "journal": paper.journal,
                    "doi": paper.doi,
                    "abstract": paper.abstract,
                    "year": paper.year,
                    "citations": paper.citation_count,
                    "created_at": paper.created_at,
                    "updated_at": paper.updated_at,
                    "user_id": paper.user_id
                }
                result["papers"].append(paper_data)
            
            return result
        except Exception as e:
            logger.error(f"获取项目 {project_id} 及其论文失败: {e}")
            raise 