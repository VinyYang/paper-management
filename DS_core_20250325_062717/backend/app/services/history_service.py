from ..database import get_db, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from ..models import UserActivity

class HistoryService:
    """用户操作历史服务"""
    
    def __init__(self):
        """初始化日志"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("HistoryService")
    
    async def add_history(
        self, 
        user_id: int, 
        action_type: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        记录用户操作历史
        
        参数:
            user_id: 用户ID
            action_type: 操作类型，如"search"、"download"等
            content: 操作内容描述
            metadata: 额外的元数据，如DOI、URL等
        
        返回:
            操作是否成功
        """
        try:
            # 获取数据库会话
            db = SessionLocal()
            
            # 创建活动记录
            activity = UserActivity(
                user_id=user_id,
                action_type=action_type,
                content=content,
                metadata=str(metadata) if metadata else None,
                created_at=datetime.utcnow()
            )
            
            # 添加到数据库
            db.add(activity)
            db.commit()
            
            self.logger.info(f"记录用户操作历史: user_id={user_id}, action_type={action_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"记录用户操作历史失败: {str(e)}")
            return False
            
        finally:
            # 关闭数据库会话
            db.close()
    
    async def get_user_history(
        self, 
        user_id: int, 
        action_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取用户操作历史
        
        参数:
            user_id: 用户ID
            action_type: 操作类型筛选
            limit: 返回记录数量限制
            
        返回:
            用户操作历史记录列表
        """
        try:
            # 获取数据库会话
            db = SessionLocal()
            
            # 构建查询
            query = db.query(UserActivity).filter(UserActivity.user_id == user_id)
            
            # 添加操作类型筛选
            if action_type:
                query = query.filter(UserActivity.action_type == action_type)
            
            # 添加排序和限制
            activities = query.order_by(UserActivity.created_at.desc()).limit(limit).all()
            
            # 转换结果为字典列表
            result = []
            for activity in activities:
                result.append({
                    "id": activity.id,
                    "user_id": activity.user_id,
                    "action_type": activity.action_type,
                    "content": activity.content,
                    "metadata": activity.metadata,
                    "created_at": activity.created_at
                })
                
            return result
            
        except Exception as e:
            self.logger.error(f"获取用户操作历史失败: {str(e)}")
            return []
            
        finally:
            # 关闭数据库会话
            db.close() 