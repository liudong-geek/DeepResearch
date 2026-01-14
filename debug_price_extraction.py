#!/usr/bin/env python3
"""调试价格提取问题"""

import asyncio
import sys
import re
sys.path.insert(0, "backend")

from mcp_servers.ecommerce.scrapers.uplift import UpliftScraper
from mcp_servers.ecommerce.scrapers.jarvis import JarvisScraper
from mcp_servers.shared.rate_limiter import RateLimiter
from mcp_servers.shared.cache_manager import CacheManager


async def debug_uplift():
    """调试 Uplift 价格提取"""
    print("=" * 80)
    print("🔍 调试 Uplift 价格提取")
    print("=" * 80)
    
    rate_limiter = RateLimiter(rate=0.5, burst=2)
    cache = CacheManager(ttl=3600)
    scraper = UpliftScraper(rate_limiter, cache)
    
    url = "https://www.upliftdesk.com/uplift-v2-standing-desk-v2-or-v2-commercial/"
    
    try:
        # 获取 HTML
        html = await scraper._fetch_html(url, use_js=True)
        
        # 提取所有价格
        price_matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', html)
        prices = list(set([float(p.replace(',', '')) for p in price_matches if p]))
        prices.sort()
        
        print(f"\n找到 {len(prices)} 个价格:")
        print(f"前 20 个: {prices[:20]}")
        
        # 分析价格分布
        print("\n价格分布:")
        print(f"  < $100: {len([p for p in prices if p < 100])}")
        print(f"  $100-$200: {len([p for p in prices if 100 <= p < 200])}")
        print(f"  $200-$500: {len([p for p in prices if 200 <= p < 500])}")
        print(f"  $500-$1000: {len([p for p in prices if 500 <= p < 1000])}")
        print(f"  $1000-$2000: {len([p for p in prices if 1000 <= p < 2000])}")
        print(f"  > $2000: {len([p for p in prices if p >= 2000])}")
        
        # 查找实际的产品价格（在 HTML 中搜索特定模式）
        print("\n搜索产品价格标签:")
        
        # 搜索常见的价格 CSS 类
        price_patterns = [
            r'class="[^"]*price[^"]*"[^>]*>\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'data-price="(\d+(?:\.\d{2})?)"',
            r'<span[^>]*price[^>]*>\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'"price":\s*(\d+(?:\.\d{2})?)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"  模式 '{pattern[:50]}...': {matches[:5]}")
        
        # 保存 HTML 片段用于分析
        print("\n保存 HTML 片段到 debug_uplift.html")
        with open("debug_uplift.html", "w", encoding="utf-8") as f:
            # 只保存包含价格的部分
            lines = html.split('\n')
            price_lines = [line for line in lines if '$' in line and any(char.isdigit() for char in line)]
            f.write('\n'.join(price_lines[:100]))  # 前 100 行
        
        # 调用实际的产品信息提取
        print("\n调用 get_product_info:")
        result = await scraper.get_product_info(url)
        print(f"  标题: {result.get('title')}")
        print(f"  价格: ${result.get('price')}")
        
    finally:
        await scraper._close_browser()


async def debug_jarvis():
    """调试 Jarvis 价格提取"""
    print("\n" + "=" * 80)
    print("🔍 调试 Jarvis 价格提取")
    print("=" * 80)
    
    rate_limiter = RateLimiter(rate=0.5, burst=2)
    cache = CacheManager(ttl=3600)
    scraper = JarvisScraper(rate_limiter, cache)
    
    url = "https://www.fully.com/standing-desks/jarvis.html"
    
    try:
        # 获取 HTML
        html = await scraper._fetch_html(url, use_js=True)
        
        # 提取所有价格
        price_matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', html)
        prices = list(set([float(p.replace(',', '')) for p in price_matches if p]))
        prices.sort()
        
        print(f"\n找到 {len(prices)} 个价格:")
        print(f"前 20 个: {prices[:20]}")
        
        # 分析价格分布
        print("\n价格分布:")
        print(f"  < $100: {len([p for p in prices if p < 100])}")
        print(f"  $100-$200: {len([p for p in prices if 100 <= p < 200])}")
        print(f"  $200-$500: {len([p for p in prices if 200 <= p < 500])}")
        print(f"  $500-$1000: {len([p for p in prices if 500 <= p < 1000])}")
        print(f"  $1000-$2000: {len([p for p in prices if 1000 <= p < 2000])}")
        print(f"  > $2000: {len([p for p in prices if p >= 2000])}")
        
        # 搜索产品价格标签
        print("\n搜索产品价格标签:")
        price_patterns = [
            r'class="[^"]*price[^"]*"[^>]*>\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'data-price="(\d+(?:\.\d{2})?)"',
            r'<span[^>]*price[^>]*>\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'"price":\s*(\d+(?:\.\d{2})?)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"  模式 '{pattern[:50]}...': {matches[:5]}")
        
        # 保存 HTML 片段
        print("\n保存 HTML 片段到 debug_jarvis.html")
        with open("debug_jarvis.html", "w", encoding="utf-8") as f:
            lines = html.split('\n')
            price_lines = [line for line in lines if '$' in line and any(char.isdigit() for char in line)]
            f.write('\n'.join(price_lines[:100]))
        
        # 调用实际的产品信息提取
        print("\n调用 get_product_info:")
        result = await scraper.get_product_info(url)
        print(f"  标题: {result.get('title')}")
        print(f"  价格: ${result.get('price')}")
        
    finally:
        await scraper._close_browser()


async def main():
    await debug_uplift()
    await debug_jarvis()
    print("\n" + "=" * 80)
    print("调试完成！请查看 debug_uplift.html 和 debug_jarvis.html")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

