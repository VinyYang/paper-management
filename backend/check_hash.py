import sqlite3
import bcrypt

def check_hash_format():
    """检查哈希密码格式"""
    try:
        # 连接数据库
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # 查询所有用户的哈希密码
        cursor.execute("SELECT id, username, hashed_password FROM users")
        users = cursor.fetchall()
        
        print("用户ID | 用户名 | 哈希密码 | 格式正确")
        print("-" * 80)
        
        for user in users:
            user_id, username, hashed_password = user
            
            # 检查哈希密码格式是否正确
            is_valid = False
            try:
                # 尝试验证一个简单密码，验证流程是否正确
                if hashed_password:
                    bcrypt.checkpw(b"test", hashed_password.encode('utf-8'))
                    is_valid = True
            except Exception as e:
                print(f"验证失败: {e}")
                
            print(f"{user_id} | {username} | {hashed_password[:20]}... | {is_valid}")
            
        conn.close()
        
    except Exception as e:
        print(f"检查哈希格式失败: {e}")

def test_bcrypt():
    """测试bcrypt功能"""
    try:
        # 测试创建哈希
        test_password = "123456"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"原始密码: {test_password}")
        print(f"哈希结果: {hashed}")
        
        # 测试验证哈希
        verified = bcrypt.checkpw(test_password.encode('utf-8'), hashed.encode('utf-8'))
        print(f"验证结果: {verified}")
        
        # 测试错误密码
        wrong_verified = bcrypt.checkpw("wrong".encode('utf-8'), hashed.encode('utf-8'))
        print(f"错误密码验证: {wrong_verified}")
        
    except Exception as e:
        print(f"测试bcrypt失败: {e}")

if __name__ == "__main__":
    print("===== 检查哈希密码格式 =====")
    check_hash_format()
    
    print("\n===== 测试bcrypt功能 =====")
    test_bcrypt() 