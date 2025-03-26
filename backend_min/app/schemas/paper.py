from pydantic import BaseModel, ConfigDict
from typing import List, Optional, ForwardRef
from datetime import datetime

class PaperBase(BaseModel):
    title: str
    authors: str
    journal: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[int] = None
    citations: Optional[int] = 0

class PaperCreate(PaperBase):
    tags: Optional[List[str]] = None

class PaperUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[int] = None
    citations: Optional[int] = None
    tags: Optional[List[str]] = None

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