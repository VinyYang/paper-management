import requests

# 服务器基础URL
BASE_URL = "http://localhost:8002"

def try_login(username, password):
    """尝试使用不同的用户名和密码登录"""
    url = f"{BASE_URL}/api/token"
    
    data = {
        "username": username,
        "password": password
    }
    
    print(f"尝试使用 {username}/{password} 登录...")
    
    try:
        response = requests.post(url, data=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"请求异常: {e}")
        return False

# 常见的密码组合
credentials = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "123456"),
    ("admin", "admin123"),
    ("江晚正愁余", "password"),
    ("江晚正愁余", "123456"),
    ("user", "password")
]

# 尝试所有组合
success = False
for username, password in credentials:
    if try_login(username, password):
        print(f"成功使用 {username}/{password} 登录")
        success = True
        break
    print("")  # 打印空行分隔

if not success:
    print("所有尝试均失败") 