import os
import requests
import logging
from getpass import getpass

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = "http://localhost:8008"

def login():
    username = input("请输入用户名: ")
    password = getpass("请输入密码: ")
    
    url = f"{BASE_URL}/api/users/token"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        logger.info("尝试登录...")
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            logger.info("登录成功")
            token = response.json().get("access_token")
            return token
        else:
            logger.error(f"登录失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logger.error(f"登录异常: {str(e)}")
        return None

def list_papers(token):
    url = f"{BASE_URL}/api/papers"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        logger.info("获取论文列表...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            papers = response.json()
            logger.info(f"成功获取论文列表，数量: {len(papers)}")
            return papers
        else:
            logger.error(f"获取论文列表失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logger.error(f"获取论文异常: {str(e)}")
        return None

def main():
    logger.info("开始测试")
    
    # 登录获取令牌
    token = login()
    if not token:
        logger.error("无法继续测试，登录失败")
        return
    
    # 获取论文列表
    papers = list_papers(token)
    if papers:
        logger.info("测试成功完成")
    else:
        logger.error("测试未通过")

if __name__ == "__main__":
    main() 