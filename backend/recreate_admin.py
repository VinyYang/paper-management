import sqlite3
import os
import sys
import logging
from passlib.context import CryptContext

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def recreate_admin_user():
    """重新创建管理员用户"""
    try:
        # 连接到数据库
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")
        logger.info(f"连接到数据库: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 删除现有的admin用户
        cursor.execute("DELETE FROM users WHERE username='admin'")
        logger.info(f"已删除 {cursor.rowcount} 个admin用户")
        
        # 创建新的密码哈希
        hashed_password = pwd_context.hash("admin123")
        logger.info(f"新的密码哈希: {hashed_password}")
        
        # 插入新的admin用户
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role, is_active, fullname, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, ('admin', 'admin@example.com', hashed_password, 'admin', 1, 'Administrator'))
        
        # 提交事务
        conn.commit()
        logger.info(f"已创建新的admin用户，ID: {cursor.lastrowid}")
        
        # 关闭连接
        conn.close()
        
    except Exception as e:
        logger.error(f"创建admin用户失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    recreate_admin_user() 