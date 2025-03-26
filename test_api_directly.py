import requests
import json
import logging
from getpass import getpass

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = "http://localhost:8008"

def login(username, password):
    """登录并获取令牌"""
    url = f"{BASE_URL}/api/users/token"
    
    try:
        # 使用正确的表单格式提交登录请求
        response = requests.post(
            url, 
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info(f"登录成功")
            return token_data["access_token"]
        else:
            logger.error(f"登录失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logger.error(f"登录请求异常: {e}")
        return None

def test_main_api(token):
    """测试主应用中的API（Form格式）"""
    url = f"{BASE_URL}/api/papers/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "title": "测试论文 - Form API",
        "authors": "测试作者",
        "journal": "测试期刊",
        "year": "2023",
        "doi": "10.1234/test.form",
        "abstract": "使用Form格式API创建的测试论文"
    }
    
    try:
        response = requests.post(url, data=data, headers=headers)
        logger.info(f"使用Form API的响应: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"Form API请求异常: {e}")

def test_router_api(token):
    """测试路由模块中的API（JSON格式）"""
    url = f"{BASE_URL}/api/papers"  # 不带尾部斜杠
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "title": "测试论文 - JSON API",
        "authors": "测试作者",
        "journal": "测试期刊",
        "year": 2023,
        "doi": "10.1234/test.json",
        "abstract": "使用JSON格式API创建的测试论文"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        logger.info(f"使用JSON API的响应: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"JSON API请求异常: {e}")

def main():
    # 获取登录凭据
    username = input("请输入用户名: ")
    password = getpass("请输入密码: ")
    
    # 登录获取令牌
    token = login(username, password)
    if not token:
        logger.error("登录失败，无法继续测试")
        return
    
    # 测试两种API
    logger.info("测试Form格式API（main.py中定义的）")
    test_main_api(token)
    
    logger.info("测试JSON格式API（router中定义的）")
    test_router_api(token)

if __name__ == "__main__":
    main() 