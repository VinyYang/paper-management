import sqlite3
import bcrypt
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 新密码
NEW_PASSWORD = "password"

try:
    # 使用bcrypt直接生成哈希
    password_bytes = NEW_PASSWORD.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    logger.info(f"生成的密码哈希: {hashed_password}")
    
    # 连接到数据库
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # 更新admin用户的密码
    cursor.execute(
        'UPDATE users SET hashed_password = ? WHERE username = ?', 
        (hashed_password, 'admin')
    )
    
    # 提交更改
    conn.commit()
    affected_rows = cursor.rowcount
    
    if affected_rows > 0:
        logger.info(f"成功更新admin用户的密码，影响行数: {affected_rows}")
    else:
        logger.warning("没有找到admin用户或密码未变更")
    
    # 验证更新
    cursor.execute('SELECT username, hashed_password FROM users WHERE username = ?', ('admin',))
    user = cursor.fetchone()
    if user:
        logger.info(f"用户: {user[0]}, 新密码哈希: {user[1]}")
        
        # 验证密码是否正确
        is_valid = bcrypt.checkpw(password_bytes, user[1].encode('utf-8'))
        logger.info(f"密码验证测试: {'成功' if is_valid else '失败'}")
    
    # 关闭连接
    conn.close()
    
    logger.info("密码重置操作完成")
    
except Exception as e:
    logger.error(f"密码重置失败: {str(e)}") 