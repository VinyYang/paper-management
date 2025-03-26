from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CitationBase(BaseModel):
    """引用基础模型"""
    paper_id: int
    cited_paper_id: int
    citation_context: Optional[str] = None
    citation_type: Optional[str] = None
    is_public: bool = False

class CitationCreate(CitationBase):
    """创建引用模型"""
    pass

class CitationUpdate(BaseModel):
    """更新引用模型"""
    citation_context: Optional[str] = None
    citation_type: Optional[str] = None
    is_public: Optional[bool] = None

class Citation(CitationBase):
    """引用完整模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 