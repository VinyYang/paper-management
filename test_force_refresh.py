import requests

# 登录获取token
def login():
    login_url = "http://localhost:8001/api/token"
    login_data = {
        "username": "test",  # 替换为你的用户名
        "password": "test123"  # 替换为你的密码
    }
    
    print(f"尝试登录: {login_url}")
    try:
        response = requests.post(login_url, data=login_data)
        print(f"登录状态码: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"登录成功，获取到token: {token[:10]}...")
            return token
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录出错: {str(e)}")
        return None

# 测试强制刷新API
def test_force_refresh(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 测试普通刷新
    refresh_url = "http://localhost:8001/api/latest-papers/refresh"
    print(f"\n测试普通刷新: {refresh_url}")
    try:
        response = requests.post(refresh_url, headers=headers)
        print(f"普通刷新 状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"普通刷新出错: {str(e)}")
    
    # 测试强制刷新
    force_refresh_url = "http://localhost:8001/api/latest-papers/force-refresh"
    print(f"\n测试强制刷新: {force_refresh_url}")
    try:
        response = requests.post(force_refresh_url, headers=headers)
        print(f"强制刷新 状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"强制刷新出错: {str(e)}")

if __name__ == "__main__":
    print("开始测试强制刷新API...")
    token = login()
    if token:
        test_force_refresh(token)
    else:
        print("无法获取令牌，测试终止") 