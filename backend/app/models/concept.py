from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base
from .paper import paper_concepts

class Concept(Base):
    """概念模型"""
    __tablename__ = "concepts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    # category = Column(Integer, default=0)  # 概念类别：0=基础概念，1=扩展概念，2=主题概念 - 暂时注释掉此字段，数据库中尚未创建
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    papers = relationship("Paper", secondary=paper_concepts, back_populates="concepts")
    user_interests = relationship("UserInterest", back_populates="concept", cascade="all, delete-orphan")
    notes = relationship("Note", secondary="note_concepts", back_populates="concepts")
    
    # 作为源概念和目标概念的关联
    source_relations = relationship("ConceptRelation", 
                                   foreign_keys="ConceptRelation.source_id",
                                   back_populates="source", 
                                   cascade="all, delete-orphan")
    target_relations = relationship("ConceptRelation", 
                                   foreign_keys="ConceptRelation.target_id",
                                   back_populates="target", 
                                   cascade="all, delete-orphan")

class ConceptRelation(Base):
    """概念之间的关系模型"""
    __tablename__ = "concept_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    relation_type = Column(String(50), nullable=False)  # 例如: is_a, part_of, related_to
    weight = Column(Float, default=1.0)  # 关系权重
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    source = relationship("Concept", foreign_keys=[source_id], back_populates="source_relations")
    target = relationship("Concept", foreign_keys=[target_id], back_populates="target_relations") 