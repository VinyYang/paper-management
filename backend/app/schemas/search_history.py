from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SearchHistoryBase(BaseModel):
    """搜索历史基础模型"""
    query: str
    search_type: str  # paper, concept, note等
    filters: Optional[dict] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    is_public: bool = False

class SearchHistoryCreate(SearchHistoryBase):
    """创建搜索历史模型"""
    pass

class SearchHistoryUpdate(BaseModel):
    """更新搜索历史模型"""
    query: Optional[str] = None
    search_type: Optional[str] = None
    filters: Optional[dict] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    is_public: Optional[bool] = None

class SearchHistory(SearchHistoryBase):
    """搜索历史完整模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 