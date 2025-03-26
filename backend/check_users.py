import sqlite3
import os
import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_users():
    """查看用户信息"""
    try:
        # 连接数据库
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # 查询所有用户
        cursor.execute('SELECT id, username, email, role, hashed_password FROM users')
        rows = cursor.fetchall()
        
        # 显示用户信息
        print("用户ID | 用户名 | 邮箱 | 角色 | 哈希密码")
        print("-" * 80)
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4][:20]}...")
            
        conn.close()
        
    except Exception as e:
        print(f"查询用户信息失败: {e}")

if __name__ == "__main__":
    check_users() 