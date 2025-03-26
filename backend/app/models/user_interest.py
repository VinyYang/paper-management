from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class UserInterest(Base):
    """用户兴趣模型，存储用户对不同概念的兴趣权重"""
    __tablename__ = "user_interests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    weight = Column(Float, default=1.0, nullable=False)  # 兴趣权重
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="interests")
    concept = relationship("Concept", back_populates="user_interests") 