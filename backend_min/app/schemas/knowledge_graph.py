from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConceptBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[int] = 0  # 概念类别：0=基础概念，1=扩展概念，2=主题概念

class ConceptCreate(ConceptBase):
    pass

class ConceptUpdate(ConceptBase):
    name: Optional[str] = None

class Concept(ConceptBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class ConceptRelationBase(BaseModel):
    source_id: int
    target_id: int
    relation_type: str
    weight: float = 1.0

class ConceptRelationCreate(ConceptRelationBase):
    pass

class ConceptRelationUpdate(BaseModel):
    relation_type: Optional[str] = None
    weight: Optional[float] = None

class ConceptRelation(ConceptRelationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class GraphNode(BaseModel):
    id: int
    name: str
    value: float = 1.0
    description: Optional[str] = None

class GraphLink(BaseModel):
    source: int
    target: int
    value: float = 1.0
    relation: str

class Graph(BaseModel):
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]

class ConceptWithRelations(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    related_concepts: List[Concept] = []
    relation_types: List[str] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

# 新添加的数据模型
class PaperSimilarity(BaseModel):
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