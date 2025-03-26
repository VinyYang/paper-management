import requests
import json

# 服务器基础URL
BASE_URL = "http://localhost:8002"

def get_token():
    """获取登录令牌"""
    url = f"{BASE_URL}/api/token"
    
    # 使用新创建的管理员用户
    form_data = {
        "username": "testadmin",
        "password": "123456"
    }
    
    # 重要：使用form参数而不是json参数
    response = requests.post(url, data=form_data)
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"登录成功: {response.text}")
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"登录失败: {response.text}")
        return None

def test_concepts(token):
    """测试获取概念列表"""
    if not token:
        print("没有有效令牌，无法继续测试")
        return
    
    url = f"{BASE_URL}/api/graph/concepts/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n获取概念列表...")
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:300]}..." if len(response.text) > 300 else f"响应内容: {response.text}")

def create_concept(token, name, description, category=0):
    """测试创建概念"""
    if not token:
        print("没有有效令牌，无法继续测试")
        return
    
    url = f"{BASE_URL}/api/graph/concepts/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    concept_data = {
        "name": name,
        "description": description,
        "category": category
    }
    
    print(f"\n创建概念: {name}...")
    response = requests.post(url, headers=headers, json=concept_data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        return response.json()
    return None

def create_relation(token, source_id, target_id, relation_type="相关", weight=0.8):
    """测试创建概念关系"""
    if not token:
        print("没有有效令牌，无法继续测试")
        return
    
    url = f"{BASE_URL}/api/graph/relations/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    relation_data = {
        "source_id": source_id,
        "target_id": target_id,
        "relation_type": relation_type,
        "weight": weight
    }
    
    print(f"\n创建关系: {source_id} -> {target_id}...")
    response = requests.post(url, headers=headers, json=relation_data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        return response.json()
    return None

if __name__ == "__main__":
    # 获取令牌
    token = get_token()
    
    if token:
        # 测试获取概念列表
        test_concepts(token)
        
        # 测试创建两个概念
        concept1 = create_concept(token, "测试概念1", "这是第一个测试概念", 1)
        concept2 = create_concept(token, "测试概念2", "这是第二个测试概念", 2)
        
        # 如果成功创建了两个概念，则测试创建关系
        if concept1 and concept2:
            create_relation(token, concept1["id"], concept2["id"], "包含", 0.9) 