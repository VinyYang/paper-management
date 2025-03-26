import requests
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = "http://localhost:8008"

def login():
    """登录并获取令牌"""
    url = f"{BASE_URL}/api/users/token"
    
    # 使用管理员凭据
    username = "admin"
    password = "password"
    
    data = {
        "username": username,
        "password": password
    }
    
    try:
        logger.info(f"使用凭据 {username}/{password} 登录...")
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info("登录成功")
            return token_data["access_token"]
        else:
            logger.error(f"登录失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logger.error(f"登录请求异常: {e}")
        return None

def create_paper(token):
    """创建一个简单的论文"""
    url = f"{BASE_URL}/api/papers/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "title": "测试论文",
        "authors": "测试作者",
        "journal": "测试期刊",
        "year": "2023",
        "doi": "10.1234/test.direct",
        "abstract": "直接测试脚本创建的论文"
    }
    
    try:
        logger.info("创建论文...")
        response = requests.post(url, data=data, headers=headers)
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        if response.status_code in [200, 201]:
            logger.info("论文创建成功!")
            return True
        else:
            logger.error(f"论文创建失败: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logger.error(f"创建论文请求异常: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始测试...")
    
    # 登录获取令牌
    token = login()
    if not token:
        logger.error("登录失败，无法继续测试")
        return
    
    # 创建论文
    create_paper(token)
    
    logger.info("测试完成")

if __name__ == "__main__":
    main() 