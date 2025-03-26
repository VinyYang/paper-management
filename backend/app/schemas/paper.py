from pydantic import BaseModel, ConfigDict
from typing import List, Optional, ForwardRef
from datetime import datetime

class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_path: Optional[str] = None
    keywords: Optional[str] = None
    journal: Optional[str] = None
    conference: Optional[str] = None
    citation_count: Optional[int] = 0
    read_count: Optional[int] = 0
    is_public: bool = False
    project_id: Optional[int] = None

class PaperCreate(PaperBase):
    citation_count: Optional[int] = 0
    tags: Optional[List[str]] = None

class PaperUpdate(PaperBase):
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_path: Optional[str] = None
    keywords: Optional[str] = None
    journal: Optional[str] = None
    conference: Optional[str] = None
    citation_count: Optional[int] = None
    read_count: Optional[int] = None
    is_public: Optional[bool] = None
    project_id: Optional[int] = None

class Paper(PaperBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class PaperWithTags(Paper):
    tags: List[str] = []

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    ) 