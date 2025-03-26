import sqlite3

def search_user(username):
    """搜索特定用户"""
    try:
        # 连接数据库
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # 查询用户
        cursor.execute("SELECT id, username, email, role, hashed_password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user:
            print(f"找到用户: ID={user[0]}, 用户名={user[1]}, 邮箱={user[2]}, 角色={user[3]}")
        else:
            print(f"未找到用户: {username}")
            
        conn.close()
        
    except Exception as e:
        print(f"查询用户失败: {e}")

if __name__ == "__main__":
    # 1. 默认搜索"江晚正愁余"
    search_user("江晚正愁余")
    # 2. 搜索testadmin
    search_user("testadmin") 