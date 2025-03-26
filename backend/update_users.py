from app.database import SessionLocal, engine
from app.models import Base, User
from sqlalchemy import Column, Integer, text
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_user_table():
    """更新User表，添加缺失的storage_used字段"""
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 检查user表中是否有storage_used列
        with engine.connect() as conn:
            # 获取user表的列信息
            # 修正：通过索引位置获取表结构信息
            table_info = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            # PRAGMA table_info返回的结果中，列名在索引1的位置
            columns = [column[1] for column in table_info]
            
            # 如果没有storage_used列，添加它
            if "storage_used" not in columns:
                logger.info("添加users表的storage_used字段...")
                conn.execute(text("ALTER TABLE users ADD COLUMN storage_used INTEGER DEFAULT 0"))
                conn.commit()
                logger.info("storage_used字段添加成功")
            else:
                logger.info("users表已有storage_used字段")
                
        # 查询所有用户，并确保storage_used有有效值
        users = db.query(User).all()
        logger.info(f"发现{len(users)}个用户")
        
        update_count = 0
        for user in users:
            if not hasattr(user, 'storage_used') or user.storage_used is None:
                user.storage_used = 0
                update_count += 1
        
        if update_count > 0:
            logger.info(f"更新了{update_count}个用户的storage_used字段")
            db.commit()
        else:
            logger.info("所有用户都已有storage_used字段")
            
        logger.info("用户表更新完成")
    except Exception as e:
        logger.error(f"更新用户表失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_user_table() 