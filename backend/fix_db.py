import logging
import sys
import traceback
from sqlalchemy import create_engine, text
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_user_activities_table():
    """修复user_activities表结构，添加缺少的activity_metadata列"""
    try:
        logger.info("开始修复user_activities表...")
        
        # 直接创建数据库连接
        engine = create_engine(settings.DATABASE_URL)
        connection = engine.connect()
        
        try:
            # 使用原始SQL查询添加列
            logger.info("尝试添加activity_metadata列...")
            connection.execute(text("ALTER TABLE user_activities ADD COLUMN activity_metadata TEXT"))
            connection.commit()
            logger.info("activity_metadata列添加成功")
            return True
        except Exception as e:
            logger.error(f"执行SQL时出错: {e}")
            logger.error(traceback.format_exc())
            return False
        finally:
            connection.close()
    except Exception as e:
        logger.error(f"修复user_activities表失败: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("开始数据库修复...")
    try:
        success = fix_user_activities_table()
        if success:
            logger.info("数据库修复完成")
        else:
            logger.error("数据库修复失败")
            sys.exit(1)
    except Exception as e:
        logger.error(f"发生意外错误: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1) 