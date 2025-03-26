from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConceptBase(BaseModel):
    """概念基础模型"""
    name: str
    description: Optional[str] = None
    category: Optional[int] = 0  # 概念类别：0=基础概念，1=扩展概念，2=主题概念

class ConceptCreate(ConceptBase):
    """创建概念模型"""
    pass

class ConceptUpdate(ConceptBase):
    """更新概念模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[int] = None

class Concept(ConceptBase):
    """概念模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConceptNode(BaseModel):
    """概念节点模型"""
    id: int
    name: str
    description: Optional[str] = None
    weight: Optional[float] = 1.0
    paper_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class ConceptRelationBase(BaseModel):
    """概念关系基础模型"""
    source_id: int
    target_id: int
    relation_type: str
    weight: float = 1.0
    description: Optional[str] = None

class ConceptRelationCreate(ConceptRelationBase):
    """创建概念关系模型"""
    pass

class ConceptRelationUpdate(BaseModel):
    """更新概念关系模型"""
    relation_type: Optional[str] = None
    weight: Optional[float] = None

class ConceptRelation(ConceptRelationBase):
    """概念关系模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GraphNode(BaseModel):
    """图谱节点模型，用于响应"""
    id: int
    name: str
    description: Optional[str] = None
    group: int = 1  # 节点分组
    weight: float = 1.0
    related_papers: List[Dict[str, Any]] = []
    related_notes: List[Dict[str, Any]] = []
    relation_types: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class GraphLink(BaseModel):
    """图谱链接模型"""
    source: int
    target: int
    value: float = 1.0
    relation: str
    
    model_config = ConfigDict(from_attributes=True)

class Graph(BaseModel):
    """知识图谱响应模型"""
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
    
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

# 新添加的数据模型
class PaperSimilarity(BaseModel):
    """论文相似度模型"""
    paper_id: int
    title: str
    authors: str
    year: Optional[int] = None
    similarity: float
    shared_concepts: int
    concept_similarity: Optional[float] = None
    title_similarity: Optional[float] = None
    author_similarity: Optional[float] = None
    venue_similarity: Optional[float] = None
    year_similarity: Optional[float] = None
    source_id: Optional[int] = None
    target_id: Optional[int] = None
    abstract_similarity: Optional[float] = None

class ConceptExtraction(BaseModel):
    paper_id: int
    title: str
    extracted_concepts: List[Dict[str, Any]]

class BatchExtractionResult(BaseModel):
    processed_count: int
    details: List[ConceptExtraction]

class RelatedPaper(BaseModel):
    id: int
    title: str
    authors: str

class PathConcept(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    related_papers: List[RelatedPaper] = []

class ReadingPath(BaseModel):
    start_concept: str
    target_concept: str
    path_length: int
    concepts: List[PathConcept]

class ReadingPathResponse(BaseModel):
    target_concept: Dict[str, Any]
    learning_paths: List[ReadingPath]

# 添加两篇论文相似度比较结果模型
class DetailedSimilarity(BaseModel):
    similarity: float
    shared_concepts: int
    concept_similarity: float
    title_similarity: float
    author_similarity: float
    venue_similarity: float
    year_similarity: float

class KnowledgeNode(BaseModel):
    """知识节点模型"""
    id: int
    name: str
    description: Optional[str] = None
    node_type: str
    data: Optional[Dict[str, Any]] = None
    weight: float = 1.0
    x: Optional[float] = None
    y: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class KnowledgeEdge(BaseModel):
    """知识边模型"""
    id: int
    source_id: int
    target_id: int
    relationship_type: str
    weight: float = 1.0
    data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class GraphDataResponse(BaseModel):
    """知识图谱数据响应模型"""
    nodes: List[KnowledgeNode]
    edges: List[KnowledgeEdge] 