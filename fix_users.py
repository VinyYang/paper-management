import os

# 创建一个临时Python脚本
script = """
import sqlite3
import bcrypt
from datetime import datetime

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# 连接数据库
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# 1. 重置管理员密码
admin_password = 'admin123'
hashed_admin_password = hash_password(admin_password)
cursor.execute('UPDATE users SET hashed_password = ? WHERE username = ?', 
              (hashed_admin_password, 'admin'))
print(f'已重置管理员密码为: {admin_password}')

# 2. 创建测试用户
test_username = 'testuser'
test_email = 'test@example.com'
test_password = 'testpassword'

# 检查用户是否已存在
cursor.execute('SELECT id FROM users WHERE username = ?', (test_username,))
if cursor.fetchone():
    print(f'用户 {test_username} 已存在，跳过创建')
else:
    # 创建新用户
    hashed_password = hash_password(test_password)
    now = datetime.utcnow()
    cursor.execute(
        'INSERT INTO users (username, email, hashed_password, role, is_active, created_at, updated_at) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (test_username, test_email, hashed_password, 'user', True, now, now)
    )
    print(f'成功创建测试用户: {test_username}，密码: {test_password}')

# 提交更改
conn.commit()
conn.close()
print('数据库操作完成')
"""

# 将脚本保存到临时文件
with open('temp_fix_users.py', 'w') as f:
    f.write(script)

# 上传并执行脚本
os.system('pscp -pw "Yhy13243546" temp_fix_users.py root@47.108.139.79:/var/www/ds/backend/')
os.system('echo y | plink -pw "Yhy13243546" "root@47.108.139.79" "cd /var/www/ds/backend && python3 temp_fix_users.py"')

# 清理临时文件
os.system('del temp_fix_users.py')
os.system('echo y | plink -pw "Yhy13243546" "root@47.108.139.79" "cd /var/www/ds/backend && rm temp_fix_users.py"')

# 重启服务
os.system('echo y | plink -pw "Yhy13243546" "root@47.108.139.79" "systemctl restart ds-backend && systemctl restart nginx"')

print("已完成用户账号修复并重启服务。现在可以使用以下账号登录：")
print("1. 管理员账号: admin / admin123")
print("2. 普通用户账号: testuser / testpassword") 