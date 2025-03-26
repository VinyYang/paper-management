from app.database import SessionLocal, engine
from sqlalchemy import text
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_user_columns():
    """添加用户表中可能缺失的列"""
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 获取用户表的列信息
        with engine.connect() as conn:
            columns = [column[1] for column in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
            
            # 需要添加的列及其默认值
            columns_to_add = {
                "first_name": "VARCHAR(50)",
                "last_name": "VARCHAR(50)",
                "avatar_url": "VARCHAR(255)",
                "fullname": "VARCHAR(100)",
                "bio": "TEXT",
                "is_active": "BOOLEAN DEFAULT 1"
            }
            
            # 检查并添加缺失的列
            for column_name, column_type in columns_to_add.items():
                if column_name not in columns:
                    logger.info(f"添加{column_name}列到users表...")
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                    logger.info(f"{column_name}列添加成功")
                else:
                    logger.info(f"users表已有{column_name}列")
            
        logger.info("数据库修改完成")
    except Exception as e:
        logger.error(f"修改数据库结构失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_user_columns() 