import requests

# 服务器地址
BASE_URL = "http://0.0.0.0:8001"

def test_login():
    """测试使用OAuth2PasswordRequestForm方式登录"""
    
    # 准备登录数据（使用form格式而不是json）
    login_data = {
        "username": "admin",
        "password": "admin123",
        "grant_type": "password"  # OAuth2需要的grant_type
    }
    
    # 发送登录请求
    try:
        # 注意使用application/x-www-form-urlencoded格式
        response = requests.post(
            f"{BASE_URL}/api/users/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # 打印响应
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 检查是否成功
        if response.status_code == 200:
            print("登录成功!")
            token_data = response.json()
            print(f"访问令牌: {token_data.get('access_token')}")
        else:
            print("登录失败!")
            print(f"响应详情: {response.text}")
    except Exception as e:
        print(f"请求出错: {str(e)}")

if __name__ == "__main__":
    test_login() 