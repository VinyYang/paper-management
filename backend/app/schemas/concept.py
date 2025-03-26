from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ConceptBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    parent_id: Optional[int] = None
    is_public: bool = False

class ConceptCreate(ConceptBase):
    pass

class ConceptUpdate(ConceptBase):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    parent_id: Optional[int] = None
    is_public: Optional[bool] = None

class Concept(ConceptBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    ) 