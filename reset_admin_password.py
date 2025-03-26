import sqlite3
import bcrypt

def hash_password(password):
    # 生成密码hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def reset_admin_password(new_password='admin123'):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # 生成新密码hash
    hashed_password = hash_password(new_password)
    
    # 更新管理员密码
    cursor.execute('UPDATE users SET hashed_password = ? WHERE username = ?', 
                  (hashed_password, 'admin'))
    
    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    
    print(f'已成功重置管理员密码为: {new_password}')

if __name__ == '__main__':
    reset_admin_password() 