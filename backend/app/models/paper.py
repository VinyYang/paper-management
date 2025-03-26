from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base
# 直接从project模块导入project_paper
from .project import project_paper

# 论文与标签的多对多关系表
paper_tag = Table(
    "paper_tag",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

# 论文与概念的多对多关系表
paper_concepts = Table(
    "paper_concepts",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
    Column("concept_id", Integer, ForeignKey("concepts.id"), primary_key=True)
)

class Paper(Base):
    """论文模型"""
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(String(1000))
    abstract = Column(Text)
    doi = Column(String(100), unique=True, index=True)
    arxiv_id = Column(String(50), index=True)
    url = Column(String(500))
    publication_date = Column(DateTime)
    venue = Column(String(255))
    journal_id = Column(Integer, ForeignKey("journals.id"))
    citation_count = Column(Integer, default=0)
    reference_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    journal = Column(String(255))  # 期刊名称冗余存储
    source = Column(String(255))  # 论文来源，如arxiv, ieee等
    year = Column(Integer)  # 出版年份冗余存储
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # 项目ID
    
    # 关系
    user = relationship("User", back_populates="papers")
    tags = relationship("Tag", secondary=paper_tag, back_populates="papers")
    # 使用已导入的project_paper
    projects = relationship("Project", secondary=project_paper, back_populates="papers")
    notes = relationship("Note", back_populates="paper", cascade="all, delete-orphan")
    reading_histories = relationship("ReadingHistory", back_populates="paper", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="paper", cascade="all, delete-orphan")
    concepts = relationship("Concept", secondary=paper_concepts, back_populates="papers")
    citations_to = relationship("Citation", foreign_keys="Citation.paper_id", back_populates="paper", cascade="all, delete-orphan")
    citations_from = relationship("Citation", foreign_keys="Citation.cited_paper_id", back_populates="cited_paper", cascade="all, delete-orphan")
    journal_relation = relationship("Journal", back_populates="papers")

class Tag(Base):
    """标签模型"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    
    # 关系
    papers = relationship("Paper", secondary=paper_tag, back_populates="tags") 