from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class JournalBase(BaseModel):
    name: str
    publisher: Optional[str] = None
    issn: Optional[str] = None
    impact_factor: Optional[float] = None
    h_index: Optional[int] = None
    description: Optional[str] = None
    website: Optional[str] = None
    abbreviation: Optional[str] = None
    ranking: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None

class JournalCreate(JournalBase):
    pass

class JournalUpdate(JournalBase):
    pass

class Journal(JournalBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class LatestPaperBase(BaseModel):
    title: str
    authors: str
    abstract: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    publish_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None

class LatestPaperCreate(LatestPaperBase):
    journal_id: int
    paper_id: Optional[int] = None

class LatestPaper(LatestPaperBase):
    id: int
    journal_id: int
    paper_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    ) 