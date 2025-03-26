from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class ActivityResponse(BaseModel):
    """用户活动响应模型"""
    id: int
    user_id: int
    activity_type: str
    target_id: Optional[int] = None
    target_type: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    is_public: bool = False
    
    model_config = ConfigDict(from_attributes=True) 