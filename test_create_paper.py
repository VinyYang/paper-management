import os
import sys
import logging
import json
import requests
from getpass import getpass

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保可以导入backend模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

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
            logger.error(f"登录失败: {response.json() if response.text else response.status_code}")
            return None
    except Exception as e:
        logger.error(f"登录请求异常: {e}")
        return None

def main():
    """主函数"""
    logger.info("开始测试论文创建功能...")
    
    # 获取登录凭据
    if len(sys.argv) > 2:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = input("请输入用户名: ")
        password = getpass("请输入密码: ")
    
    # 登录获取令牌
    token = login(username, password)
    if not token:
        logger.error("登录失败，无法继续测试")
        return
    
    # 创建论文
    paper_data = {
        "title": "测试论文 - API测试",
        "authors": "测试作者",
        "journal": "测试期刊",
        "year": "2023",
        "doi": "10.1234/test.paper",
        "abstract": "这是一篇测试论文的摘要"
    }
    
    # 直接发送请求
    url = f"{BASE_URL}/api/papers/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, data=paper_data, headers=headers)
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        if response.status_code in [200, 201]:
            logger.info("论文创建成功!")
        else:
            logger.error(f"论文创建失败: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"创建论文请求异常: {e}")
    
    logger.info("论文创建功能测试完成")

if __name__ == "__main__":
    main() 