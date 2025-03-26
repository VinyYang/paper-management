import os

# 复制后端的reset_admin_password.py文件到服务器
os.system('echo y | plink -pw "Yhy13243546" "root@47.108.139.79" "cd /var/www/ds/backend && cat > reset_password.py << \'EOF\'\
import sqlite3\n\
import bcrypt\n\
\n\
def hash_password(password):\n\
    # 生成密码hash\n\
    salt = bcrypt.gensalt()\n\
    hashed = bcrypt.hashpw(password.encode(\'utf-8\'), salt)\n\
    return hashed.decode(\'utf-8\')\n\
\n\
def reset_admin_password(new_password=\'admin123\'):\n\
    conn = sqlite3.connect(\'app.db\')\n\
    cursor = conn.cursor()\n\
    \n\
    # 生成新密码hash\n\
    hashed_password = hash_password(new_password)\n\
    \n\
    # 更新管理员密码\n\
    cursor.execute(\'UPDATE users SET hashed_password = ? WHERE username = ?\', \
                  (hashed_password, \'admin\'))\n\
    \n\
    # 提交更改并关闭连接\n\
    conn.commit()\n\
    conn.close()\n\
    \n\
    print(f\'已成功重置管理员密码为: {new_password}\')\n\
\n\
if __name__ == \'__main__\':\n\
    reset_admin_password()\n\
EOF"')

# 执行重置密码脚本
os.system('echo y | plink -pw "Yhy13243546" "root@47.108.139.79" "cd /var/www/ds/backend && python3 reset_password.py"')

print("管理员密码已重置为：admin123") 