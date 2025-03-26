from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class UserActivityBase(BaseModel):
    """用户活动基础模型"""
    activity_type: str  # read_paper, create_note, search, etc.
    target_id: Optional[int] = None  # 相关资源的ID（如论文ID、笔记ID等）
    target_type: Optional[str] = None  # 相关资源的类型（如paper、note等）
    details: Optional[Dict[str, Any]] = None  # 活动详情
    is_public: bool = False

class UserActivityCreate(UserActivityBase):
    """创建用户活动模型"""
    pass

class UserActivityUpdate(BaseModel):
    """更新用户活动模型"""
    activity_type: Optional[str] = None
    target_id: Optional[int] = None
    target_type: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None

class UserActivity(UserActivityBase):
    """用户活动完整模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 