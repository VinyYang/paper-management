from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class Citation(Base):
    """引用关系模型"""
    __tablename__ = "citations"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    cited_paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    citation_text = Column(String(500))  # 引用文本片段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    paper = relationship("Paper", foreign_keys=[paper_id], back_populates="citations_to")
    cited_paper = relationship("Paper", foreign_keys=[cited_paper_id], back_populates="citations_from") 