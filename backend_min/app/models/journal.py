from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class Journal(Base):
    """期刊模型"""
    __tablename__ = "journals"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    publisher = Column(String(255))
    issn = Column(String(20))  
    impact_factor = Column(Float)
    h_index = Column(Integer)
    description = Column(Text)
    website = Column(String(255))
    abbreviation = Column(String(50))
    ranking = Column(String(50))    # 期刊评级，如A+、A、B等
    category = Column(String(100))  # 类别，如AI、ML、CV等
    url = Column(String(500))       # 期刊网站
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    latest_papers = relationship("LatestPaper", back_populates="journal")
    papers = relationship("Paper", back_populates="journal_relation")

class LatestPaper(Base):
    """最新论文模型，用于存储从期刊爬取的最新论文信息"""
    __tablename__ = "latest_papers"
    
    id = Column(Integer, primary_key=True)
    journal_id = Column(Integer, ForeignKey("journals.id"))
    paper_id = Column(Integer, ForeignKey("papers.id"))
    title = Column(String(500))  # 添加标题字段
    authors = Column(String(1000))  # 添加作者字段
    abstract = Column(Text)  # 添加摘要字段
    url = Column(String(500))  # 添加URL字段
    doi = Column(String(100))  # 添加DOI字段
    publish_date = Column(DateTime)
    publication_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    journal = relationship("Journal", back_populates="latest_papers") 