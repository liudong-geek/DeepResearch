#!/usr/bin/env python3
"""
单独测试 Monoprice（Cloudflare 挑战）
"""

import asyncio
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from loguru import logger
from mcp_servers.shared import RateLimiter, CacheManager
from mcp_servers.ecommerce.scrapers import MonopriceScraper


async def main():
    """测试 Monoprice"""
    
    logger.info("="*60)
    logger.info("测试 Monoprice（Cloudflare 挑战）")
    logger.info("="*60)
    
    # 创建爬虫
    rate_limiter = RateLimiter(rate=0.5, burst=2)
    cache = CacheManager(ttl=3600)
    scraper = MonopriceScraper(rate_limiter, cache)
    
    url = "https://www.monoprice.com/product?p_id=15722"
    
    try:
        logger.info(f"\n正在抓取: {url}\n")
        
        # 抓取产品信息
        result = await scraper.get_product_info(url)
        
        # 检查结果
        if 'error' in result:
            logger.error(f"❌ 抓取失败: {result['error']}")
            logger.info("\n可能的原因:")
            logger.info("1. Cloudflare 5s 挑战需要更高级的绕过技术")
            logger.info("2. 建议使用 FlareSolverr 或 undetected-chromedriver")
            logger.info("3. 或者使用代理 IP 池")
        else:
            logger.success(f"✅ 抓取成功!")
            logger.info(f"\n产品信息:")
            logger.info(f"  标题: {result.get('title', 'N/A')}")
            logger.info(f"  价格: ${result.get('price', 'N/A')}")
            logger.info(f"  描述: {result.get('description', 'N/A')[:100]}...")
            logger.info(f"  图片: {result.get('image_url', 'N/A')[:80]}...")
            
    except Exception as e:
        logger.error(f"❌ 抓取异常: {e}")
    finally:
        # 清理浏览器
        await scraper._close_browser()


if __name__ == "__main__":
    asyncio.run(main())

