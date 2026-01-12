#!/usr/bin/env python3
"""
测试所有电商爬虫
"""
import asyncio
import sys
import os

# 添加 backend 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_all_scrapers():
    """测试所有爬虫"""
    from mcp_servers.ecommerce.server import EcommerceMCPServer
    
    print("="*60)
    print("🧪 测试所有电商爬虫")
    print("="*60)
    
    # 创建 MCP Server
    server = EcommerceMCPServer()
    
    # 测试 URL
    test_cases = [
        {
            "brand": "uplift",
            "url": "https://www.upliftdesk.com/uplift-v2-standing-desk-v2-or-v2-commercial/",
            "name": "Uplift V2 Standing Desk"
        },
        {
            "brand": "jarvis",
            "url": "https://www.fully.com/standing-desks/jarvis.html",
            "name": "Jarvis Standing Desk"
        },
        {
            "brand": "vari",
            "url": "https://www.vari.com/electric-standing-desk-60x30/FD-ESD6030.html",
            "name": "Vari Electric Standing Desk"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"📍 测试 {i}/{len(test_cases)}: {test_case['name']}")
        print(f"   品牌: {test_case['brand']}")
        print(f"   URL: {test_case['url']}")
        print(f"{'='*60}")
        
        try:
            # 调用工具
            result = await server.call_tool(
                "get_product_info",
                {
                    "brand": test_case["brand"],
                    "url": test_case["url"]
                }
            )
            
            # 解析结果
            if isinstance(result, list) and len(result) > 0:
                data = result[0].text
                
                # 尝试解析 JSON
                import json
                try:
                    product_data = json.loads(data)
                    
                    print(f"\n✅ 成功获取产品信息:")
                    print(f"   品牌: {product_data.get('brand', 'N/A')}")
                    print(f"   标题: {product_data.get('title', 'N/A')}")
                    print(f"   价格: ${product_data.get('price', 0)}")
                    print(f"   货币: {product_data.get('currency', 'N/A')}")
                    
                    desc = product_data.get('description', '')
                    if desc:
                        print(f"   描述: {desc[:80]}...")
                    
                    img_url = product_data.get('image_url', '')
                    if img_url:
                        print(f"   图片: {img_url[:80]}...")
                    
                    print(f"   库存: {'有货' if product_data.get('in_stock') else '缺货'}")
                    
                    results.append({
                        "brand": test_case["brand"],
                        "success": True,
                        "data": product_data
                    })
                    
                except json.JSONDecodeError:
                    print(f"\n⚠️  返回数据不是 JSON:")
                    print(f"   {data[:200]}...")
                    results.append({
                        "brand": test_case["brand"],
                        "success": False,
                        "error": "Invalid JSON"
                    })
            else:
                print(f"\n❌ 未获取到数据")
                results.append({
                    "brand": test_case["brand"],
                    "success": False,
                    "error": "No data returned"
                })
                
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "brand": test_case["brand"],
                "success": False,
                "error": str(e)
            })
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    print(f"\n成功: {success_count}/{total_count}")
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['brand'].capitalize()}")
        if not result["success"]:
            print(f"   错误: {result.get('error', 'Unknown')}")
    
    # 关闭浏览器
    for scraper in server.scrapers.values():
        await scraper._close_browser()
    
    print(f"\n{'='*60}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_scrapers())

