from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class ConceptNode(BaseModel):
    """知识图谱节点模型"""
    id: int
    name: str
    description: Optional[str] = None
    weight: Optional[float] = 1.0
    paper_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class ConceptEdge(BaseModel):
    """知识图谱边模型"""
    id: int
    source_id: int
    target_id: int
    relationship_type: str
    weight: float = 1.0
    source_name: Optional[str] = None
    target_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class GraphResponse(BaseModel):
    """知识图谱响应模型"""
    nodes: List[ConceptNode]
    edges: List[ConceptEdge]

class ConceptDetail(BaseModel):
    """概念详情模型"""
    id: int
    name: str
    description: Optional[str] = None
    weight: Optional[float] = 1.0
    paper_count: int = 0
    related_concepts: List[ConceptNode] = []
    
    model_config = ConfigDict(from_attributes=True)

class ConceptRelationCreate(BaseModel):
    """创建概念关系模型"""
    source_id: int
    target_id: int
    relationship_type: str
    weight: Optional[float] = 1.0

class ConceptRelationUpdate(BaseModel):
    """更新概念关系模型"""
    relationship_type: Optional[str] = None
    weight: Optional[float] = None 