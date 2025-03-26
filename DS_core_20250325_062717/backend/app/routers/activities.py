from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..dependencies import get_db, get_current_user
from ..models import User, UserActivity
from ..schemas.activity import ActivityResponse

router = APIRouter(
    prefix="/activities",
    tags=["activities"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.get("/", response_model=List[ActivityResponse])
async def get_user_activities(
    skip: int = 0,
    limit: int = 100,
    activity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的活动记录"""
    try:
        # 构建查询
        query = db.query(UserActivity).filter(UserActivity.user_id == current_user.id)
        
        # 应用过滤条件
        if activity_type:
            query = query.filter(UserActivity.activity_type == activity_type)
        if start_date:
            query = query.filter(UserActivity.created_at >= start_date)
        if end_date:
            query = query.filter(UserActivity.created_at <= end_date)
        
        # 按时间倒序排序并分页
        activities = query.order_by(UserActivity.created_at.desc()).offset(skip).limit(limit).all()
        
        return activities
    except Exception as e:
        logger.error(f"获取用户活动记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户活动记录失败: {str(e)}")

@router.get("/types", response_model=List[str])
async def get_activity_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的所有活动类型"""
    try:
        # 获取用户的所有活动类型
        activity_types = db.query(UserActivity.activity_type).filter(
            UserActivity.user_id == current_user.id
        ).distinct().all()
        
        return [type[0] for type in activity_types]
    except Exception as e:
        logger.error(f"获取活动类型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取活动类型失败: {str(e)}")

@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用户活动记录"""
    try:
        # 检查活动记录是否存在
        activity = db.query(UserActivity).filter(
            UserActivity.id == activity_id,
            UserActivity.user_id == current_user.id
        ).first()
        
        if not activity:
            raise HTTPException(status_code=404, detail="活动记录不存在或无权访问")
        
        # 删除活动记录
        db.delete(activity)
        db.commit()
        
        return {"detail": "活动记录已成功删除"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除活动记录失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除活动记录失败: {str(e)}")

@router.delete("/")
async def clear_activities(
    activity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """清除用户的活动记录"""
    try:
        # 构建查询
        query = db.query(UserActivity).filter(UserActivity.user_id == current_user.id)
        
        # 如果指定了活动类型，只清除该类型的记录
        if activity_type:
            query = query.filter(UserActivity.activity_type == activity_type)
        
        # 删除记录
        query.delete()
        db.commit()
        
        return {"detail": "活动记录已成功清除"}
    except Exception as e:
        db.rollback()
        logger.error(f"清除活动记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清除活动记录失败: {str(e)}") 