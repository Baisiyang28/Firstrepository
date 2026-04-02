#!/usr/bin/env python3
"""
测试新API功能的脚本
"""

import urllib.request
import json
import sys

def test_api(url, method='GET', data=None):
    """测试API端点"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        else:
            req = urllib.request.Request(url)

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ {url} - 成功")
            return result
    except Exception as e:
        print(f"❌ {url} - 失败: {e}")
        return None

def main():
    """主测试函数"""
    base_url = "http://localhost:5000"

    print("🧪 测试AI Agent论坛新API功能")
    print("=" * 50)

    # 测试统计API
    print("\n📊 测试统计API:")
    stats = test_api(f"{base_url}/api/stats")
    if stats:
        print(f"   论坛统计: {stats}")

    # 测试话题API
    print("\n📋 测试话题API:")
    topics = test_api(f"{base_url}/api/topic/list")
    if topics and 'topics' in topics:
        print(f"   话题数量: {len(topics['topics'])}")
        if topics['topics']:
            print(f"   第一个话题: {topics['topics'][0]['title']}")

    # 测试工具API
    print("\n🛠️ 测试工具API:")
    tools = test_api(f"{base_url}/api/tool/list")
    if tools and 'tools' in tools:
        print(f"   工具数量: {len(tools['tools'])}")
        if tools['tools']:
            print(f"   第一个工具: {tools['tools'][0]['name']}")

    # 测试活跃用户API
    print("\n👥 测试活跃用户API:")
    users = test_api(f"{base_url}/api/active_users?limit=5")
    if users and 'users' in users:
        print(f"   活跃用户数量: {len(users['users'])}")

    print("\n" + "=" * 50)
    print("🎉 API测试完成！")

if __name__ == '__main__':
    main()