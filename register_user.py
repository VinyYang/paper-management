import os

# 在服务器上创建一个临时注册脚本
os.system('echo y | plink -pw "Yhy13243546" "root@47.108.139.79" "cd /var/www/ds/backend && cat > register_temp.py << \'EOF\'\
import sqlite3\n\
import bcrypt\n\
from datetime import datetime\n\
\n\
def hash_password(password):\n\
    salt = bcrypt.gensalt()\n\
    hashed = bcrypt.hashpw(password.encode(\'utf-8\'), salt)\n\
    return hashed.decode(\'utf-8\')\n\
\n\
def create_user(username, email, password, role=\'user\'):\n\
    conn = sqlite3.connect(\'app.db\')\n\
    cursor = conn.cursor()\n\
    \n\
    # 检查用户名是否存在\n\
    cursor.execute(\'SELECT id FROM users WHERE username = ?\', (username,))\n\
    if cursor.fetchone():\n\
        print(f\'用户名 {username} 已存在\')\n\
        conn.close()\n\
        return False\n\
    \n\
    # 检查邮箱是否存在\n\
    cursor.execute(\'SELECT id FROM users WHERE email = ?\', (email,))\n\
    if cursor.fetchone():\n\
        print(f\'邮箱 {email} 已被注册\')\n\
        conn.close()\n\
        return False\n\
    \n\
    # 生成密码hash\n\
    hashed_password = hash_password(password)\n\
    now = datetime.utcnow()\n\
    \n\
    # 插入新用户\n\
    cursor.execute(\n\
        \'INSERT INTO users (username, email, hashed_password, role, is_active, created_at, updated_at) \'\n\
        \'VALUES (?, ?, ?, ?, ?, ?, ?)\',\n\
        (username, email, hashed_password, role, True, now, now)\n\
    )\n\
    \n\
    conn.commit()\n\
    user_id = cursor.lastrowid\n\
    conn.close()\n\
    \n\
    print(f\'成功创建用户 {username} (ID: {user_id})\')\n\
    return True\n\
\n\
# 创建测试用户\n\
if __name__ == \'__main__\':\n\
    create_user(\'testuser\', \'test@example.com\', \'testpassword\')\n\
EOF"')

# 执行注册脚本
os.system('echo y | plink -pw "Yhy13243546" "root@47.108.139.79" "cd /var/www/ds/backend && python3 register_temp.py"')

print("已尝试注册测试用户：testuser / testpassword") 