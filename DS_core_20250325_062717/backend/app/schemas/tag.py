from pydantic import BaseModel, ConfigDict
from typing import Optional

class TagBase(BaseModel):
    """标签基础模型"""
    name: str

class TagCreate(TagBase):
    """创建标签的请求模型"""
    pass

class TagResponse(TagBase):
    """标签响应模型"""
    id: int

    model_config = ConfigDict(from_attributes=True) 