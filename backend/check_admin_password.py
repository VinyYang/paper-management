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

def check_admin_password():
    """检查admin用户的密码"""
    try:
        # 连接到数据库
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")
        logger.info(f"连接到数据库: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询admin用户
        cursor.execute("SELECT id, username, hashed_password FROM users WHERE username='admin'")
        user = cursor.fetchone()
        
        if user:
            logger.info(f"找到admin用户: ID={user[0]}")
            logger.info(f"密码哈希: {user[2]}")
            
            # 尝试验证密码
            test_passwords = ["admin", "admin123", "password", "123456"]
            for password in test_passwords:
                is_valid = pwd_context.verify(password, user[2])
                logger.info(f"密码 '{password}' 是否正确: {is_valid}")
                
            # 创建新密码哈希
            new_hashed_password = pwd_context.hash("admin123")
            logger.info(f"新的密码哈希 (admin123): {new_hashed_password}")
            
            # 更新密码
            update = input("是否更新admin用户的密码为'admin123'? (y/n): ")
            if update.lower() == 'y':
                cursor.execute("UPDATE users SET hashed_password=? WHERE username='admin'", (new_hashed_password,))
                conn.commit()
                logger.info("密码已更新")
        else:
            logger.info("未找到admin用户")
        
        # 关闭连接
        conn.close()
        
    except Exception as e:
        logger.error(f"检查密码失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    check_admin_password() 