import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def list_tables():
    """列出数据库中的所有表"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect('./app.db')
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            logger.info("数据库中的表:")
            for i, table in enumerate(tables, 1):
                logger.info(f"{i}. {table[0]}")
        else:
            logger.info("数据库中没有表")
        
        conn.close()
    except Exception as e:
        logger.error(f"列出表时出错: {str(e)}")

if __name__ == "__main__":
    logger.info("开始查询数据库表...")
    list_tables() 