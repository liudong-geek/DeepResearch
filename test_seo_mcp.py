#!/usr/bin/env python3
"""测试 SEO MCP Server"""

import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加 backend 到路径
import sys
sys.path.insert(0, "backend")

from mcp_servers.seo import SEOMCPServer


async def test_seo_mcp():
    """测试 SEO MCP Server"""
    
    print("🧪 测试 SEO MCP Server\n")
    
    # 检查环境变量
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not api_key or not engine_id:
        print("⚠️  警告: Google Search API 未配置")
        print("   请在 .env 文件中设置:")
        print("   - GOOGLE_SEARCH_API_KEY")
        print("   - GOOGLE_SEARCH_ENGINE_ID")
        print("\n   获取方式:")
        print("   1. API Key: https://developers.google.com/custom-search/v1/overview")
        print("   2. Search Engine ID: https://programmablesearchengine.google.com/")
        print("\n   免费配额: 100 次/天")
        print("\n   继续测试（将返回空结果）...\n")
    
    # 初始化 SEO MCP Server
    server = SEOMCPServer()
    
    # 测试 1: Google 搜索
    print("=" * 60)
    print("测试 1: Google 搜索")
    print("=" * 60)
    
    result = await server.call_tool(
        "google_search",
        {
            "query": "standing desk",
            "market": "us",
            "num_results": 5
        }
    )
    
    if result and len(result) > 0:
        import json
        data = json.loads(result[0].text)
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ 找到 {len(data)} 个搜索结果:\n")
            for i, item in enumerate(data[:3], 1):
                print(f"{i}. {item.get('title')}")
                print(f"   URL: {item.get('link')}")
                print(f"   摘要: {item.get('snippet', '')[:100]}...")
                print()
        else:
            print("⚠️  未获取到搜索结果（可能未配置 API 或配额已用完）")
    else:
        print("❌ 搜索失败")
    
    # 测试 2: 竞品排名分析
    print("\n" + "=" * 60)
    print("测试 2: 竞品排名分析")
    print("=" * 60)
    
    result = await server.call_tool(
        "analyze_competitor_rankings",
        {
            "keyword": "standing desk",
            "competitors": ["Uplift", "Jarvis", "Vari", "FlexiSpot"],
            "market": "us"
        }
    )
    
    if result and len(result) > 0:
        import json
        data = json.loads(result[0].text)
        
        print(f"关键词: {data.get('keyword')}")
        print(f"市场: {data.get('market')}")
        print(f"洞察: {data.get('insights')}\n")
        
        rankings = data.get('rankings', {})
        if rankings:
            print("竞品排名:")
            for brand, info in rankings.items():
                print(f"  {brand}: 第 {info['position']} 名")
                print(f"    标题: {info['title']}")
                print(f"    URL: {info['url']}")
                print()
        else:
            print("⚠️  未找到竞品排名（可能未配置 API 或配额已用完）")
    else:
        print("❌ 分析失败")
    
    # 测试 3: SERP 特性
    print("\n" + "=" * 60)
    print("测试 3: SERP 特性")
    print("=" * 60)
    
    result = await server.call_tool(
        "get_serp_features",
        {
            "query": "best standing desk",
            "market": "us"
        }
    )
    
    if result and len(result) > 0:
        import json
        data = json.loads(result[0].text)
        
        print(f"查询: {data.get('query')}")
        print(f"总结果数: {data.get('total_results', 0)}\n")
        
        top_results = data.get('top_results', [])
        if top_results:
            print("Top 3 结果:")
            for i, item in enumerate(top_results, 1):
                print(f"{i}. {item.get('title')}")
                print(f"   URL: {item.get('url')}")
                print()
        else:
            print("⚠️  未获取到结果（可能未配置 API 或配额已用完）")
    else:
        print("❌ 获取失败")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_seo_mcp())

