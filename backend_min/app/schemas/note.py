from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str
    page_number: Optional[int] = None

class NoteCreate(NoteBase):
    paper_id: int

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    page_number: Optional[int] = None

class Note(NoteBase):
    id: int
    user_id: int
    paper_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class NoteWithConcepts(Note):
    concept_ids: List[int] = []
    concept_names: List[str] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True 