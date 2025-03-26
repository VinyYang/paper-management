import requests
import json

# 服务器基础URL
BASE_URL = "http://localhost:8002"

def get_token():
    """获取登录令牌"""
    url = f"{BASE_URL}/api/token"
    
    # 使用江晚正愁余/123456登录
    data = {
        "username": "江晚正愁余",
        "password": "123456"
    }
    
    # 使用requests库的form参数
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        if "access_token" in token_data:
            print(f"成功获取令牌: {token_data['access_token'][:20]}...")
            return token_data["access_token"]
    
    print(f"获取令牌失败: {response.status_code} - {response.text}")
    return None

# 获取令牌
TOKEN = get_token()
if not TOKEN:
    print("无法获取令牌，测试终止")
    exit(1)

# 设置请求头
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_create_concept():
    """测试创建概念"""
    url = f"{BASE_URL}/api/graph/concepts/"
    
    # 概念数据
    concept_data = {
        "name": "人工智能测试",
        "description": "这是一个测试概念",
        "category": 1
    }
    
    # 发送请求
    response = requests.post(url, headers=headers, json=concept_data)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    return response.json() if response.status_code == 200 else None

def test_create_relation():
    """测试创建概念关系"""
    url = f"{BASE_URL}/api/graph/relations/"
    
    # 获取概念列表
    concepts_response = requests.get(f"{BASE_URL}/api/graph/concepts/", headers=headers)
    if concepts_response.status_code != 200:
        print(f"获取概念列表失败: {concepts_response.status_code}")
        return None
    
    concepts = concepts_response.json()
    if len(concepts) < 2:
        print("概念数量不足，无法创建关系")
        return None
    
    # 使用前两个概念创建关系
    relation_data = {
        "source_id": concepts[0]["id"],
        "target_id": concepts[1]["id"],
        "relation_type": "相关",
        "weight": 0.8
    }
    
    # 发送请求
    response = requests.post(url, headers=headers, json=relation_data)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    return response.json() if response.status_code == 200 else None

def test_get_concepts():
    """测试获取概念列表"""
    url = f"{BASE_URL}/api/graph/concepts/"
    
    # 发送请求
    response = requests.get(url, headers=headers)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}...") # 只打印前500个字符
    
    return response.json() if response.status_code == 200 else None

def test_get_graph():
    """测试获取知识图谱"""
    url = f"{BASE_URL}/api/graph/graph"
    
    # 发送请求
    response = requests.get(url, headers=headers)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容长度: {len(response.text)}")
    print(f"概要内容: {response.text[:200]}...") # 只打印前200个字符
    
    return response.json() if response.status_code == 200 else None

if __name__ == "__main__":
    print("测试获取概念列表...")
    test_get_concepts()
    
    print("\n测试创建概念...")
    created_concept = test_create_concept()
    
    print("\n测试创建概念关系...")
    created_relation = test_create_relation()
    
    print("\n测试获取知识图谱...")
    test_get_graph() 