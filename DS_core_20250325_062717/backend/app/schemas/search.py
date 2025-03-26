from pydantic import BaseModel
from typing import List, Optional

class SearchResult(BaseModel):
    title: str
    authors: List[str]
    year: int
    journal: Optional[str] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    source: str
    has_pdf: bool = False 