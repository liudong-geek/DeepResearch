#!/usr/bin/env python3
"""
Reddit API 测试脚本

测试 Reddit API 配置是否正确
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

def test_reddit_api():
    """测试 Reddit API 配置"""
    
    print("=" * 60)
    print("Reddit API 配置测试")
    print("=" * 60)
    
    # 检查环境变量
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "DeepResearch/1.0")
    
    print("\n📋 配置检查:")
    print(f"  Client ID: {client_id[:5]}..." if client_id else "  ❌ Client ID: Not found")
    print(f"  Client Secret: {client_secret[:5]}..." if client_secret else "  ❌ Client Secret: Not found")
    print(f"  User Agent: {user_agent}")
    
    if not client_id or not client_secret:
        print("\n" + "=" * 60)
        print("❌ Reddit API 凭证未配置")
        print("=" * 60)
        print("\n请按照以下步骤配置:")
        print("1. 访问 https://www.reddit.com/prefs/apps")
        print("2. 创建一个新的 'script' 类型应用")
        print("3. 获取 Client ID 和 Client Secret")
        print("4. 在 backend/.env 中配置:")
        print("   REDDIT_CLIENT_ID=your_client_id")
        print("   REDDIT_CLIENT_SECRET=your_client_secret")
        print("   REDDIT_USER_AGENT=DeepResearch/1.0 by YourUsername")
        print("\n详细教程: docs/REDDIT_API_SETUP.md")
        return False
    
    # 尝试导入 praw
    try:
        import praw
    except ImportError:
        print("\n" + "=" * 60)
        print("❌ PRAW 库未安装")
        print("=" * 60)
        print("\n请运行以下命令安装:")
        print("  cd backend")
        print("  source .venv/bin/activate")
        print("  pip install praw")
        return False
    
    # 测试连接
    print("\n🔌 测试连接...")
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # 测试获取子版块
        subreddit = reddit.subreddit("StandingDesk")
        print(f"✅ 成功连接到 r/{subreddit.display_name}")
        print(f"   订阅者: {subreddit.subscribers:,}")
        
        # 测试获取帖子
        print("\n📝 获取热门帖子 (前 5 个):")
        for i, post in enumerate(subreddit.hot(limit=5), 1):
            print(f"  {i}. {post.title[:60]}...")
            print(f"     评分: {post.score} | 评论: {post.num_comments}")
        
        print("\n" + "=" * 60)
        print("🎉 Reddit API 测试成功！")
        print("=" * 60)
        print("\n你现在可以使用 Reddit API 获取更稳定的数据。")
        print("DeepResearch 会自动使用 PRAW 而不是 JSON API。")
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ Reddit API 测试失败")
        print("=" * 60)
        print(f"\n错误信息: {e}")
        print("\n可能的原因:")
        print("1. Client ID 或 Secret 不正确")
        print("2. 网络连接问题")
        print("3. Reddit API 服务异常")
        print("\n请检查配置并重试。")
        return False


def test_json_api_fallback():
    """测试 JSON API 后备方案"""
    
    print("\n" + "=" * 60)
    print("测试 JSON API 后备方案")
    print("=" * 60)
    
    try:
        import httpx
        import asyncio
        
        async def fetch_json():
            async with httpx.AsyncClient() as client:
                url = "https://www.reddit.com/r/StandingDesk/hot.json?limit=3"
                headers = {
                    "User-Agent": "DeepResearch/1.0"
                }
                response = await client.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    
                    print(f"\n✅ JSON API 可用 (获取到 {len(posts)} 个帖子)")
                    for i, post in enumerate(posts, 1):
                        post_data = post.get("data", {})
                        print(f"  {i}. {post_data.get('title', 'N/A')[:60]}...")
                    return True
                else:
                    print(f"\n⚠️ JSON API 返回 {response.status_code}")
                    print("这可能是 Reddit 的反爬虫机制。")
                    print("建议配置 Reddit API 以获得更稳定的服务。")
                    return False
        
        return asyncio.run(fetch_json())
        
    except Exception as e:
        print(f"\n❌ JSON API 测试失败: {e}")
        return False


if __name__ == "__main__":
    print("\n")
    
    # 测试 Reddit API
    api_success = test_reddit_api()
    
    # 如果 API 失败，测试 JSON API 后备方案
    if not api_success:
        print("\n" + "-" * 60)
        json_success = test_json_api_fallback()
        
        if json_success:
            print("\n💡 提示:")
            print("JSON API 目前可用，但不稳定。")
            print("强烈建议配置 Reddit API 以获得更好的体验。")
        else:
            print("\n⚠️ 警告:")
            print("Reddit API 和 JSON API 都不可用。")
            print("请配置 Reddit API 或检查网络连接。")
    
    print("\n")

