#!/usr/bin/env python3
"""测试 Humanscale 爬虫"""

import asyncio
import sys
sys.path.insert(0, "backend")

from mcp_servers.ecommerce import EcommerceMCPServer


async def test_humanscale():
    """测试 Humanscale 产品信息抓取"""
    
    print("🧪 测试 Humanscale 爬虫\n")
    
    # 初始化 E-commerce MCP Server
    server = EcommerceMCPServer()
    
    # 测试 URL
    test_url = "https://www.humanscale.com/products/standing-desks/quickstand-eco-desk-converter"
    
    print(f"📍 测试 URL: {test_url}\n")
    print("=" * 60)
    
    try:
        # 调用工具
        result = await server.call_tool(
            "get_product_info",
            {
                "brand": "humanscale",
                "url": test_url
            }
        )
        
        # 解析结果
        if result and len(result) > 0:
            import json
            data = json.loads(result[0].text)
            
            print("\n✅ 成功获取产品信息:\n")
            print(f"品牌: {data.get('brand', 'N/A')}")
            print(f"标题: {data.get('title', 'N/A')}")
            print(f"价格: ${data.get('price', 0)}")
            print(f"货币: {data.get('currency', 'N/A')}")
            
            # 价格元数据
            print(f"\n价格置信度: {data.get('price_confidence', 'N/A')}")
            print(f"提取方法: {data.get('price_extraction_method', 'N/A')}")
            
            if data.get('price_warning'):
                print(f"⚠️  警告: {data.get('price_warning')}")
            
            desc = data.get('description', '')
            if desc:
                print(f"\n描述: {desc[:200]}...")
            
            img_url = data.get('image_url', '')
            if img_url:
                print(f"\n图片: {img_url}")
            
            print(f"\n库存: {'有货' if data.get('in_stock') else '缺货'}")
            
            # 检查是否有错误
            if 'error' in data:
                print(f"\n❌ 错误: {data['error']}")
        else:
            print("❌ 未获取到结果")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理浏览器
        for scraper in server.scrapers.values():
            await scraper._close_browser()
    
    print("\n" + "=" * 60)
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(test_humanscale())

