from pydantic import BaseModel, ConfigDict, TypeAdapter
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class PaperInProject(BaseModel):
    id: int
    title: str
    authors: str
    journal: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[int] = None
    citations: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class Project(ProjectBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectWithPapers(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    papers: List[PaperInProject] = []

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

# 重建模型以解决Pydantic v2类型定义问题
TypeAdapter(ProjectWithPapers).validate_python({
    "id": 1,
    "name": "示例项目",
    "user_id": 1,
    "created_at": datetime.now(),
    "papers": []
}) 