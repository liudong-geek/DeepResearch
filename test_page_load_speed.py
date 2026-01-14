#!/usr/bin/env python3
"""测试页面加载速度优化"""

import asyncio
import sys
import time
sys.path.insert(0, "backend")

from mcp_servers.ecommerce import EcommerceMCPServer


async def test_page_load_speed():
    """测试多个品牌的页面加载速度"""
    
    print("🧪 测试页面加载速度优化\n")
    
    # 初始化 E-commerce MCP Server
    server = EcommerceMCPServer()
    
    # 测试 URL
    test_cases = [
        {
            "brand": "uplift",
            "url": "https://www.upliftdesk.com/uplift-v2-standing-desk-v2-or-v2-commercial/",
            "name": "Uplift V2"
        },
        {
            "brand": "vari",
            "url": "https://www.vari.com/electric-standing-desk-60x30/FD-ESD6030.html",
            "name": "Vari Electric"
        },
        {
            "brand": "jarvis",
            "url": "https://www.fully.com/standing-desks/jarvis.html",
            "name": "Jarvis"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"📍 测试 {i}/{len(test_cases)}: {test_case['name']}")
        print(f"   品牌: {test_case['brand']}")
        print(f"   URL: {test_case['url']}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # 调用工具
            result = await server.call_tool(
                "get_product_info",
                {
                    "brand": test_case["brand"],
                    "url": test_case["url"]
                }
            )
            
            elapsed = time.time() - start_time
            
            # 解析结果
            if result and len(result) > 0:
                import json
                data = json.loads(result[0].text)
                
                success = 'error' not in data
                price = data.get('price', 0)
                
                print(f"\n✅ 成功 (耗时: {elapsed:.1f}s)")
                print(f"   标题: {data.get('title', 'N/A')[:60]}...")
                print(f"   价格: ${price}")
                
                if data.get('price_warning'):
                    print(f"   ⚠️  {data.get('price_warning')}")
                
                results.append({
                    "brand": test_case["brand"],
                    "success": success,
                    "elapsed": elapsed,
                    "price": price
                })
            else:
                elapsed = time.time() - start_time
                print(f"\n❌ 失败 (耗时: {elapsed:.1f}s)")
                results.append({
                    "brand": test_case["brand"],
                    "success": False,
                    "elapsed": elapsed,
                    "price": 0
                })
        
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n❌ 错误 (耗时: {elapsed:.1f}s): {e}")
            results.append({
                "brand": test_case["brand"],
                "success": False,
                "elapsed": elapsed,
                "price": 0,
                "error": str(e)
            })
    
    # 清理浏览器
    for scraper in server.scrapers.values():
        await scraper._close_browser()
    
    # 统计结果
    print("\n" + "="*60)
    print("📊 测试结果统计")
    print("="*60)
    
    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    avg_time = sum(r["elapsed"] for r in results) / total if total > 0 else 0
    
    print(f"\n总测试数: {total}")
    print(f"成功: {success_count}/{total} ({success_count/total*100:.0f}%)")
    print(f"平均耗时: {avg_time:.1f}s")
    
    print("\n详细结果:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['brand']:12s} - {r['elapsed']:5.1f}s - ${r.get('price', 0)}")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_page_load_speed())

