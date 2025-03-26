from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserInterestBase(BaseModel):
    """用户兴趣基础模型"""
    concept_id: int
    weight: float = 1.0  # 兴趣权重
    is_public: bool = False

class UserInterestCreate(UserInterestBase):
    """创建用户兴趣模型"""
    pass

class UserInterestUpdate(BaseModel):
    """更新用户兴趣模型"""
    concept_id: Optional[int] = None
    weight: Optional[float] = None
    is_public: Optional[bool] = None

class UserInterest(UserInterestBase):
    """用户兴趣完整模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 