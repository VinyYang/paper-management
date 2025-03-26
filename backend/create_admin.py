import sqlite3
import os
import bcrypt
import datetime

def create_admin_user():
    """创建一个新的管理员用户"""
    try:
        # 连接到数据库
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # 准备用户数据
        username = "testadmin"
        email = "testadmin@example.com"
        password = "123456"
        role = "admin"
        
        # 检查用户是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"用户 {username} 已存在")
            conn.close()
            return False
        
        # 哈希密码
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 创建当前时间
        now = datetime.datetime.utcnow().isoformat()
        
        # 插入用户
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role, created_at, updated_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, email, hashed_password, role, now, now, True))
        
        # 提交并关闭
        conn.commit()
        
        # 验证用户是否创建成功
        cursor.execute("SELECT id, username, email, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            print(f"管理员用户创建成功: ID={user[0]}, 用户名={user[1]}, 邮箱={user[2]}, 角色={user[3]}")
            print(f"密码: {password}")
        else:
            print("用户创建失败")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        return False

if __name__ == "__main__":
    create_admin_user() 