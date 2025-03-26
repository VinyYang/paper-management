import sys
import os
from pathlib import Path
import asyncio
import httpx
import json
from pprint import pprint

# 设置项目根目录到系统路径
ROOT_DIR = Path(__file__).parent
API_BASE_URL = "http://localhost:8000"
TOKEN = None  # 需要实际测试时替换为有效的认证令牌

async def test_get_concepts():
    """测试获取概念列表接口"""
    print("===== 测试获取概念列表 =====")
    
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        try:
            response = await client.get("/api/concepts/", headers=headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("获取到的概念列表:")
                pprint(data)
                return data
            else:
                print(f"获取概念列表失败: {response.text}")
                return None
        except Exception as e:
            print(f"请求异常: {str(e)}")
            return None

async def test_create_concept(name, description=""):
    """测试创建概念接口"""
    print(f"\n===== 测试创建概念: {name} =====")
    
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        try:
            response = await client.post(
                "/api/concepts/", 
                json={"name": name, "description": description},
                headers=headers
            )
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print("创建的概念:")
                pprint(data)
                return data
            else:
                print(f"创建概念失败: {response.text}")
                return None
        except Exception as e:
            print(f"请求异常: {str(e)}")
            return None

async def test_create_relation(source_id, target_id, relation_type):
    """测试创建关系接口"""
    print(f"\n===== 测试创建关系: {source_id} -> {target_id} ({relation_type}) =====")
    
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        try:
            response = await client.post(
                "/api/relations/", 
                json={
                    "source_id": source_id,
                    "target_id": target_id,
                    "relation_type": relation_type
                },
                headers=headers
            )
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print("创建的关系:")
                pprint(data)
                return data
            else:
                print(f"创建关系失败: {response.text}")
                return None
        except Exception as e:
            print(f"请求异常: {str(e)}")
            return None

async def test_get_graph():
    """测试获取整个知识图谱接口"""
    print("\n===== 测试获取知识图谱 =====")
    
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        try:
            response = await client.get("/api/graph/", headers=headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("获取到的知识图谱:")
                print(f"节点数量: {len(data.get('nodes', []))}")
                print(f"关系数量: {len(data.get('links', []))}")
                # 只打印前5个节点和关系作为示例
                if data.get('nodes'):
                    print("\n节点示例:")
                    pprint(data['nodes'][:5])
                if data.get('links'):
                    print("\n关系示例:")
                    pprint(data['links'][:5])
                return data
            else:
                print(f"获取知识图谱失败: {response.text}")
                return None
        except Exception as e:
            print(f"请求异常: {str(e)}")
            return None

async def main():
    print("开始测试知识图谱API...\n")
    
    # 1. 获取现有概念列表
    concepts_data = await test_get_concepts()
    
    # 2. 创建测试概念
    concept1 = await test_create_concept("机器学习", "一种人工智能的子领域，专注于开发能够从数据中学习的算法")
    concept2 = await test_create_concept("深度学习", "机器学习的一个分支，使用多层神经网络进行学习")
    
    if concept1 and concept2:
        # 3. 创建概念之间的关系
        relation = await test_create_relation(
            concept1.get('id'), 
            concept2.get('id'), 
            "包含"
        )
    
    # 4. 获取更新后的知识图谱
    graph_data = await test_get_graph()
    
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(main()) 