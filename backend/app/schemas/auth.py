from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """访问令牌模型"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None

class UserCreate(BaseModel):
    """用户创建模型"""
    username: str
    email: EmailStr
    password: str
    fullname: Optional[str] = None
    bio: Optional[str] = None

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str

class UserProfile(BaseModel):
    """用户信息模型"""
    id: int
    username: str
    email: EmailStr
    fullname: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    } 