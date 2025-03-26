from app.database import SessionLocal, engine
from sqlalchemy import text
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_storage_columns():
    """添加storage_used和storage_capacity列到users表"""
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 获取用户表的列信息
        with engine.connect() as conn:
            columns = [column[1] for column in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
            
            # 添加storage_used列
            if "storage_used" not in columns:
                logger.info("添加storage_used列到users表...")
                conn.execute(text("ALTER TABLE users ADD COLUMN storage_used INTEGER DEFAULT 0"))
                conn.commit()
                logger.info("storage_used列添加成功")
            else:
                logger.info("users表已有storage_used列")
                
            # 添加storage_capacity列
            if "storage_capacity" not in columns:
                logger.info("添加storage_capacity列到users表...")
                conn.execute(text("ALTER TABLE users ADD COLUMN storage_capacity INTEGER DEFAULT 1024"))
                conn.commit()
                logger.info("storage_capacity列添加成功")
            else:
                logger.info("users表已有storage_capacity列")
            
            # 更新现有记录，确保字段有默认值
            logger.info("确保现有用户记录的存储字段有默认值...")
            conn.execute(text("UPDATE users SET storage_used = 0 WHERE storage_used IS NULL"))
            conn.execute(text("UPDATE users SET storage_capacity = 1024 WHERE storage_capacity IS NULL"))
            conn.commit()
            logger.info("现有用户记录更新完成")
            
        logger.info("数据库修改完成")
    except Exception as e:
        logger.error(f"修改数据库结构失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_storage_columns() 