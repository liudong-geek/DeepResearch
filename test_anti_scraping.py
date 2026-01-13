#!/usr/bin/env python3
"""
测试反爬虫改进效果
"""

import asyncio
import sys
import os

# 添加 backend 到路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from loguru import logger
from mcp_servers.shared import RateLimiter, CacheManager
from mcp_servers.ecommerce.scrapers import GenericScraper


async def test_brand(brand_name: str, url: str):
    """测试单个品牌"""
    logger.info(f"\n{'='*60}")
    logger.info(f"测试品牌: {brand_name}")
    logger.info(f"URL: {url}")
    logger.info(f"{'='*60}\n")
    
    # 创建爬虫
    rate_limiter = RateLimiter(rate=0.5, burst=2)
    cache = CacheManager(ttl=3600)
    scraper = GenericScraper(brand_name, rate_limiter, cache)
    
    try:
        # 抓取产品信息
        result = await scraper.get_product_info(url)
        
        # 检查结果
        if 'error' in result:
            logger.error(f"❌ {brand_name} 抓取失败: {result['error']}")
            return False
        else:
            logger.success(f"✅ {brand_name} 抓取成功!")
            logger.info(f"  标题: {result.get('title', 'N/A')}")
            logger.info(f"  价格: ${result.get('price', 'N/A')}")
            logger.info(f"  描述: {result.get('description', 'N/A')[:100]}...")
            logger.info(f"  图片: {result.get('image_url', 'N/A')[:80]}...")
            return True
            
    except Exception as e:
        logger.error(f"❌ {brand_name} 抓取异常: {e}")
        return False
    finally:
        # 清理浏览器
        await scraper._close_browser()


async def main():
    """测试所有新增品牌"""
    
    brands = [
        ("FlexiSpot", "https://www.flexispot.com/height-adjustable-desks/electric-height-adjustable-standing-desk-e7"),
        ("Autonomous", "https://www.autonomous.ai/standing-desks/smartdesk-2-home"),
        ("Humanscale", "https://www.humanscale.com/products/sit-stand-desks/float-height-adjustable-desk"),
        ("Monoprice", "https://www.monoprice.com/product?p_id=15722"),
        ("IKEA", "https://www.ikea.com/us/en/p/bekant-desk-sit-stand-white-s49022538/"),
    ]
    
    results = {}
    
    for brand_name, url in brands:
        success = await test_brand(brand_name, url)
        results[brand_name] = success
        
        # 等待一下，避免请求过快
        await asyncio.sleep(2)
    
    # 打印总结
    logger.info(f"\n{'='*60}")
    logger.info("测试总结")
    logger.info(f"{'='*60}\n")
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for brand_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        logger.info(f"{brand_name:15s} {status}")
    
    logger.info(f"\n成功率: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
    
    if success_count == total_count:
        logger.success("\n🎉 所有品牌抓取成功！")
    elif success_count >= total_count * 0.8:
        logger.warning(f"\n⚠️  大部分品牌抓取成功 ({success_count}/{total_count})")
    else:
        logger.error(f"\n❌ 抓取成功率较低 ({success_count}/{total_count})")


if __name__ == "__main__":
    asyncio.run(main())

