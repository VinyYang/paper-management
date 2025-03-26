from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ReadingHistoryBase(BaseModel):
    paper_id: int
    duration: Optional[int] = None
    interaction_type: Optional[str] = None
    rating: Optional[float] = None

class ReadingHistoryCreate(ReadingHistoryBase):
    pass

class ReadingHistory(ReadingHistoryBase):
    id: int
    user_id: int
    read_time: datetime

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class RecommendationBase(BaseModel):
    paper_id: int
    score: float
    reason: str
    is_read: bool = False

class RecommendationCreate(RecommendationBase):
    pass

class Recommendation(RecommendationBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class RecommendationWithPaper(Recommendation):
    paper_title: str
    paper_authors: str
    paper_abstract: Optional[str] = None
    paper_year: Optional[int] = None
    paper_citations: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    ) 