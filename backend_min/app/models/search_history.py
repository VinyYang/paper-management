from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class SearchHistory(Base):
    """用户搜索历史记录模型"""
    __tablename__ = "search_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query = Column(String(255), nullable=False, comment="搜索查询内容")
    result_info = Column(Text, nullable=True, comment="搜索结果信息摘要")
    doi = Column(String(255), nullable=True, comment="DOI标识符")
    url = Column(String(512), nullable=True, comment="结果URL")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="search_histories") 