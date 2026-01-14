#!/usr/bin/env python3
"""测试 SEO MCP 修复"""

import asyncio
import sys
sys.path.insert(0, "backend")

from mcp_servers.seo import SEOMCPServer


async def test_seo_fix():
    """测试 SEO MCP 的 analyze_competitor_rankings 工具"""
    
    print("🧪 测试 SEO MCP 修复\n")
    
    # 初始化 SEO MCP Server
    server = SEOMCPServer()
    
    print("=" * 60)
    print("测试: analyze_competitor_rankings")
    print("=" * 60)
    
    try:
        # 调用工具
        result = await server.call_tool(
            "analyze_competitor_rankings",
            {
                "keyword": "standing desk",
                "competitors": ["Uplift", "Jarvis", "Vari", "FlexiSpot"],
                "market": "us"
            }
        )
        
        # 解析结果
        if result and len(result) > 0:
            import json
            data = json.loads(result[0].text)
            
            print(f"\n✅ 工具调用成功\n")
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
                print("⚠️  未找到竞品排名")
                if 'error' in data:
                    print(f"    错误: {data['error']}")
                else:
                    print("    原因: Google Search API 未配置或配额已用完")
        else:
            print("❌ 工具调用失败：未返回结果")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_seo_fix())

