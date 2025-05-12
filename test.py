#!/usr/bin/env python3
"""
RAG服务测试脚本
用于测试RAG服务的功能是否正常
"""

import requests
import json
import sys
import argparse

def test_health(base_url):
    """测试健康检查接口"""
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 健康检查接口测试通过")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查接口测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 健康检查接口测试出错: {str(e)}")
        return False

def test_direct_query(base_url):
    """测试直接查询接口"""
    payload = {
        "query": "什么是人工智能?",
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print("测试直接查询接口...")
        response = requests.post(f"{base_url}/query", json=payload)
        if response.status_code == 200:
            print("✅ 直接查询接口测试通过")
            result = response.json()
            print(f"   查询: {payload['query']}")
            print(f"   响应内容片段: {result['choices'][0]['text'][:100]}...")
            return True
        else:
            print(f"❌ 直接查询接口测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 直接查询接口测试出错: {str(e)}")
        return False

def test_rag_query(base_url):
    """测试RAG查询接口"""
    payload = {
        "query": "谁是爱因斯坦?",
        "max_tokens": 100,
        "temperature": 0.7,
        "top_k": 2
    }
    
    try:
        print("测试RAG查询接口...")
        response = requests.post(f"{base_url}/rag", json=payload)
        if response.status_code == 200:
            print("✅ RAG查询接口测试通过")
            result = response.json()
            print(f"   查询: {payload['query']}")
            print(f"   检索到的上下文数量: {len(result['contexts'])}")
            print(f"   响应内容片段: {result['llm_response']['choices'][0]['text'][:100]}...")
            return True
        else:
            print(f"❌ RAG查询接口测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ RAG查询接口测试出错: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='测试RAG服务')
    parser.add_argument('--host', default='localhost', help='RAG服务主机名')
    parser.add_argument('--port', default=8000, type=int, help='RAG服务端口')
    
    args = parser.parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    print(f"开始测试RAG服务: {base_url}")
    
    # 测试健康检查
    if not test_health(base_url):
        print("健康检查失败，终止测试")
        sys.exit(1)
    
    # 测试直接查询
    test_direct_query(base_url)
    
    # 测试RAG查询
    test_rag_query(base_url)
    
    print("测试完成!")

if __name__ == "__main__":
    main()