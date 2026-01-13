#!/usr/bin/env python3
"""
测试方案A的改进效果
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_start_research():
    """测试启动调研（使用新增的竞品）"""
    print("=" * 60)
    print("测试 1: 启动调研（包含新增竞品）")
    print("=" * 60)
    
    payload = {
        "keyword": "standing desk",
        "market": "US",
        "competitors": ["Uplift", "FlexiSpot", "IKEA"]  # 包含新增的竞品
    }
    
    print(f"\n请求数据: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/research/start", json=payload)
    
    print(f"\n响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 调研已启动")
        print(f"Task ID: {data['task_id']}")
        print(f"状态: {data['status']}")
        return data['task_id']
    else:
        print(f"❌ 启动失败: {response.text}")
        return None


def test_check_status(task_id):
    """测试查询状态"""
    print("\n" + "=" * 60)
    print("测试 2: 查询调研状态")
    print("=" * 60)
    
    max_attempts = 60  # 最多等待 60 秒
    
    for i in range(max_attempts):
        response = requests.get(f"{BASE_URL}/api/research/status/{task_id}")
        
        if response.status_code == 200:
            data = response.json()
            status = data['status']
            progress = data['progress']
            current_step = data['current_step']
            
            print(f"\r进度: {progress}% | 状态: {status} | 步骤: {current_step}", end="")
            
            if status == "completed":
                print("\n✅ 调研完成！")
                return True
            elif status == "failed":
                print(f"\n❌ 调研失败: {data.get('error', 'Unknown error')}")
                return False
        
        time.sleep(1)
    
    print("\n⚠️  超时")
    return False


def test_get_result(task_id):
    """测试获取结果（检查新增字段）"""
    print("\n" + "=" * 60)
    print("测试 3: 获取调研结果（检查新增字段）")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/research/result/{task_id}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n✅ 成功获取结果")
        
        # 检查 metadata
        print("\n📊 Metadata:")
        metadata = data.get('comparison_table', {}).get('metadata', {})
        if metadata:
            print(f"  - 竞品数量: {metadata.get('total_competitors', 'N/A')}")
            print(f"  - 数据来源: {metadata.get('data_sources', 'N/A')}")
            print(f"  - 置信度: {metadata.get('confidence', 'N/A')}")
        else:
            print("  ⚠️  未找到 metadata 字段")
        
        # 检查 sources
        print("\n📚 数据来源:")
        sources = data.get('comparison_table', {}).get('sources', [])
        if sources:
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {source.get('brand', 'N/A')}")
                print(f"     URL: {source.get('url', 'N/A')}")
                print(f"     数据点: {', '.join(source.get('data_points', []))}")
                print(f"     抓取时间: {source.get('extracted_at', 'N/A')}")
        else:
            print("  ⚠️  未找到 sources 字段")
        
        # 检查 price_comparison 中的 source_url
        print("\n💰 价格对比（检查 source_url）:")
        price_comparison = data.get('comparison_table', {}).get('price_comparison', {})
        if price_comparison:
            for brand, info in price_comparison.items():
                print(f"  - {brand}:")
                print(f"    价格: ${info.get('price', 'N/A')}")
                print(f"    定位: {info.get('positioning', 'N/A')}")
                source_url = info.get('source_url', None)
                if source_url:
                    print(f"    ✅ 来源: {source_url}")
                else:
                    print(f"    ⚠️  缺少 source_url")
        else:
            print("  ⚠️  未找到 price_comparison 字段")
        
        # 保存完整结果
        with open('test_result.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\n💾 完整结果已保存到 test_result.json")
        
        return True
    else:
        print(f"❌ 获取失败: {response.text}")
        return False


def main():
    print("\n🚀 开始测试方案A的改进效果\n")
    
    # 测试 1: 启动调研
    task_id = test_start_research()
    if not task_id:
        print("\n❌ 测试失败：无法启动调研")
        return
    
    # 测试 2: 查询状态
    success = test_check_status(task_id)
    if not success:
        print("\n❌ 测试失败：调研未完成")
        return
    
    # 测试 3: 获取结果
    success = test_get_result(task_id)
    if not success:
        print("\n❌ 测试失败：无法获取结果")
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 打开 http://localhost:3000 查看前端改进")
    print("2. 查看 test_result.json 检查数据结构")
    print("3. 如果遇到反爬虫问题，暂时跳过该竞品")


if __name__ == "__main__":
    main()

