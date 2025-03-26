from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas
from ..dependencies import get_db, get_current_user
from ..models import User, Paper, Concept, ReadingHistory, Recommendation
from ..schemas.recommendation import (
    ReadingHistoryCreate,
    ReadingHistory as ReadingHistorySchema,
    RecommendationWithPaper
)
from ..services.recommendation_service import RecommendationService
from datetime import datetime
from sqlalchemy import func, case

router = APIRouter()

@router.post("/reading-history/", response_model=ReadingHistorySchema)
async def record_reading_history(
    history_data: ReadingHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查论文是否存在
    paper = db.query(Paper).filter(Paper.id == history_data.paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文不存在"
        )
    
    # 创建阅读历史记录
    recommendation_service = RecommendationService()
    reading_history = recommendation_service.record_reading_history(
        db=db,
        user_id=current_user.id,
        paper_id=history_data.paper_id,
        duration=history_data.duration,
        interaction_type=history_data.interaction_type,
        rating=history_data.rating
    )
    
    return reading_history

@router.get("/reading-history/", response_model=List[ReadingHistorySchema])
async def get_reading_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return history

@router.get("/", response_model=List[RecommendationWithPaper])
async def get_recommendations(
    limit: int = 10,
    refresh: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 如果请求刷新或者没有现有推荐，则生成新的推荐
    if refresh or db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).count() == 0:
        # 清除现有推荐
        db.query(Recommendation).filter(
            Recommendation.user_id == current_user.id
        ).delete()
        db.commit()
        
        # 生成新推荐
        recommendation_service = RecommendationService()
        recommendation_service.generate_recommendations(db=db, user_id=current_user.id)
    
    # 获取推荐列表
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).order_by(Recommendation.score.desc()).limit(limit).all()
    
    return recommendations

@router.put("/{recommendation_id}/read", response_model=RecommendationWithPaper)
async def mark_recommendation_as_read(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推荐不存在或无权访问"
        )
    
    recommendation.is_read = True
    db.commit()
    db.refresh(recommendation)
    
    return recommendation

@router.get("/statistics/", response_model=dict)
async def get_recommendation_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取阅读历史统计
    total_read = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == current_user.id
    ).count()
    
    # 获取推荐统计
    total_recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).count()
    
    read_recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.is_read == True
    ).count()
    
    # 计算平均评分
    average_rating = 0
    ratings = db.query(ReadingHistory.rating).filter(
        ReadingHistory.user_id == current_user.id,
        ReadingHistory.rating != None
    ).all()
    
    if ratings:
        average_rating = sum(r[0] for r in ratings) / len(ratings)
    
    return {
        "total_read": total_read,
        "total_recommendations": total_recommendations,
        "read_recommendations": read_recommendations,
        "average_rating": round(average_rating, 2)
    }

@router.get("/interests/", response_model=List[dict])
async def get_user_interests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的兴趣分析"""
    service = RecommendationService()
    interests = service.get_user_interests(db, current_user.id)
    
    # 获取概念名称
    concepts = db.query(Concept).filter(Concept.id.in_(interests.keys())).all() if interests else []
    concept_map = {c.id: c.name for c in concepts}
    
    # 转换为前端需要的格式
    return [
        {
            "concept": concept_map.get(cid, "未知概念"),
            "weight": weight
        }
        for cid, weight in sorted(interests.items(), key=lambda x: x[1], reverse=True)
    ]

@router.get("/random/")
async def get_random_recommendations(
    category: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取随机推荐论文，可以按照领域过滤"""
    recommendation_service = RecommendationService()
    random_recommendations = recommendation_service.get_random_recommendations(
        db=db, 
        user_id=current_user.id, 
        category=category, 
        limit=limit
    )
    
    # 包装结果为与getRecommendations相同的结构
    return {"recommendations": random_recommendations} 