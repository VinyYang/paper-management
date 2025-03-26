from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class NoteBase(BaseModel):
    """笔记基础模型"""
    title: str
    content: str
    paper_id: Optional[int] = None
    is_public: bool = False

class NoteCreate(NoteBase):
    """创建笔记的请求模型"""
    pass

class NoteUpdate(NoteBase):
    """更新笔记的请求模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    paper_id: Optional[int] = None
    is_public: Optional[bool] = None

class NoteResponse(NoteBase):
    """笔记响应模型"""
    id: int
    user_id: int
    paper_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Note(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NoteWithConcepts(Note):
    concept_ids: List[int] = []
    concept_names: List[str] = []

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    ) 