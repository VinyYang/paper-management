from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

# 论文-概念关联表
paper_concepts = Table(
    'paper_concepts',
    Base.metadata,
    Column('paper_id', Integer, ForeignKey('papers.id')),
    Column('concept_id', Integer, ForeignKey('concepts.id')),
    Column('weight', Float, default=1.0)
)

# 笔记-概念关联表
note_concepts = Table(
    'note_concepts',
    Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id')),
    Column('concept_id', Integer, ForeignKey('concepts.id')),
    Column('weight', Float, default=1.0)
)

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    papers = relationship("Paper", secondary=paper_concepts, back_populates="concepts")
    notes = relationship("Note", secondary=note_concepts, back_populates="concepts")
    # 作为源概念的关系
    source_relations = relationship(
        "ConceptRelation",
        back_populates="source_concept",
        foreign_keys="ConceptRelation.source_id"
    )
    # 作为目标概念的关系
    target_relations = relationship(
        "ConceptRelation",
        back_populates="target_concept",
        foreign_keys="ConceptRelation.target_id"
    )
    # 用户兴趣关系
    user_interests = relationship("UserInterest", back_populates="concept")

class ConceptRelation(Base):
    __tablename__ = "concept_relations"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("concepts.id"))
    target_id = Column(Integer, ForeignKey("concepts.id"))
    relation_type = Column(String(50))
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    source_concept = relationship("Concept", back_populates="source_relations", foreign_keys=[source_id])
    target_concept = relationship("Concept", back_populates="target_relations", foreign_keys=[target_id]) 