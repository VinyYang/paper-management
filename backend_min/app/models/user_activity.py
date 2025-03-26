from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class UserActivity(Base):
    """用户操作活动记录模型"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(50), nullable=False, comment="操作类型，如search, download等")
    content = Column(Text, nullable=False, comment="操作内容描述")
    activity_metadata = Column(Text, nullable=True, comment="额外的元数据，如DOI、URL等")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="activities") 