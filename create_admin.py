import os
import sys
import logging
import sqlite3
from passlib.context import CryptContext

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """创建或重置管理员用户"""
    try:
        # 连接数据库
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        
        # 检查users表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logger.error("users表不存在，请先初始化数据库")
            return False
        
        # 检查管理员用户是否存在
        cursor.execute("SELECT id, username FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        # 生成新密码哈希
        hashed_password = pwd_context.hash("password")
        
        if admin:
            admin_id = admin[0]
            logger.info(f"管理员用户已存在 (ID: {admin_id})，重置密码...")
            
            # 更新密码和激活状态
            cursor.execute(
                "UPDATE users SET hashed_password = ?, is_active = 1 WHERE id = ?",
                (hashed_password, admin_id)
            )
            conn.commit()
            logger.info("管理员密码已重置为'password'")
        else:
            logger.info("管理员用户不存在，创建新管理员用户...")
            
            # 创建新管理员用户
            cursor.execute(
                """
                INSERT INTO users (
                    username, email, hashed_password, role, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                ("admin", "admin@example.com", hashed_password, "ADMIN", 1)
            )
            conn.commit()
            logger.info("新管理员用户已创建 (username: admin, password: password)")
        
        # 显示所有用户
        logger.info("当前系统中的所有用户:")
        cursor.execute("SELECT id, username, role, is_active FROM users")
        users = cursor.fetchall()
        for user in users:
            logger.info(f"ID: {user[0]}, 用户名: {user[1]}, 角色: {user[2]}, 激活: {user[3]}")
        
        return True
    except Exception as e:
        logger.error(f"创建管理员用户失败: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    logger.info("开始创建/重置管理员用户...")
    result = create_admin_user()
    if result:
        logger.info("管理员用户操作完成")
    else:
        logger.error("管理员用户操作失败") 