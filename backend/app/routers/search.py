from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..schemas.search import SearchResult
from ..services.scholar import search_scholar, search_scihub, search_easyscholar
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.get("/scholar", response_model=List[SearchResult])
async def search_scholar_papers(
    q: str,
    current_user = Depends(get_current_user)
):
    """
    搜索Google Scholar论文
    """
    try:
        results = await search_scholar(q)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scihub", response_model=List[SearchResult])
async def search_scihub_papers(
    q: str,
    author: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    搜索Sci-Hub论文
    """
    try:
        results = await search_scihub(q, author)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/easyscholar", response_model=List[SearchResult])
async def search_easyscholar_papers(
    q: str,
    current_user = Depends(get_current_user)
):
    """
    搜索EasyScholar论文
    """
    try:
        results = await search_easyscholar(q)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 