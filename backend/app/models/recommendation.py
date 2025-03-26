from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

# 用户阅读历史表
class ReadingHistory(Base):
    __tablename__ = "reading_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    read_time = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, default=0)  # 阅读时长(秒)
    interaction_type = Column(String(50))  # 交互类型：阅读、收藏、引用等
    rating = Column(Float)  # 用户评分(1-5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="reading_histories")
    paper = relationship("Paper", back_populates="reading_histories")

# 推荐结果表
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, default=0.0)  # 推荐分数
    reason = Column(Text)  # 推荐理由
    is_read = Column(Boolean, default=False)  # 是否已读
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="recommendations")
    paper = relationship("Paper", back_populates="recommendations") 