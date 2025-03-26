import sqlite3
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists(conn, table_name):
    """检查表是否存在"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def check_column_exists(conn, table_name, column_name):
    """检查列是否存在于表中"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)

def update_database():
    """更新数据库结构"""
    logger.info("开始更新数据库结构...")
    
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), "app.db")
    
    if not os.path.exists(db_path):
        logger.error(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        
        # 检查concepts表是否存在
        if check_table_exists(conn, "concepts"):
            logger.info("找到concepts表")
            
            # 检查category列是否存在
            if not check_column_exists(conn, "concepts", "category"):
                logger.info("在concepts表中添加category列...")
                conn.execute("ALTER TABLE concepts ADD COLUMN category INTEGER DEFAULT 0")
                conn.commit()
                logger.info("成功添加category列")
            else:
                logger.info("category列已存在，无需添加")
        else:
            logger.warning("concepts表不存在，无法添加category列")
        
        conn.close()
        logger.info("数据库结构更新完成")
        return True
    
    except Exception as e:
        logger.error(f"更新数据库时发生错误: {e}")
        return False

if __name__ == "__main__":
    success = update_database()
    if success:
        print("数据库更新成功")
    else:
        print("数据库更新失败") 