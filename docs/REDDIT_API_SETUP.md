# Reddit API 申请和配置指南

> **更新时间**: 2026-01-13  
> **难度**: ⭐⭐ (中等)  
> **预计时间**: 10-15 分钟

---

## 🎯 为什么需要 Reddit API？

目前 DeepResearch 使用 Reddit 的公开 JSON API（无需认证），但存在以下限制：

- ❌ 请求频率限制严格（可能返回 403）
- ❌ 无法访问某些受限内容
- ❌ 无法获取用户信息

使用官方 Reddit API 后：

- ✅ 更高的请求限额（60 次/分钟）
- ✅ 访问更多内容
- ✅ 更稳定的服务

---

## 📋 申请步骤

### 第 1 步: 创建 Reddit 账号

1. 访问 [Reddit](https://www.reddit.com/)
2. 点击右上角 "Sign Up" 注册账号
3. 验证邮箱

**提示**: 如果已有账号，直接登录即可。

---

### 第 2 步: 创建 Reddit App

1. **访问应用管理页面**
   - 登录后访问: https://www.reddit.com/prefs/apps
   - 或者: 点击右上角头像 → Settings → Safety & Privacy → Apps

2. **创建新应用**
   - 滚动到页面底部
   - 点击 "Create App" 或 "Create Another App" 按钮

3. **填写应用信息**
   ```
   Name: DeepResearch Bot

   App type: 选择 "script" ← 重要！

   Description:
   Personal research tool for analyzing standing desk discussions

   About URL: (留空或填写 https://github.com/yourusername/deepresearch)

   Permissions: (留空)

   Redirect URI: http://localhost:8080
   ```

4. **回答问题**（可能会出现）

   **Q: What benefit/purpose will the bot/app have for Redditors?**

   **推荐回答**（选择一个）:

   **方案 1 - 简洁版（推荐）**:
   ```
   This app helps analyze product discussions and reviews on Reddit
   to provide better product recommendations for consumers researching
   standing desks.
   ```

   **方案 2 - 个人使用版**:
   ```
   Personal research tool to read and analyze standing desk discussions
   on Reddit for my own purchasing decision.
   ```

   **方案 3 - 学术研究版**:
   ```
   Academic research tool for analyzing consumer discussions about
   standing desks on Reddit to understand market trends and user
   preferences.
   ```

   **Q: Provide a detailed description of what the Bot/App will be doing on the Reddit platform.**

   **推荐回答**（选择一个）:

   **方案 1 - 详细版（推荐）**:
   ```
   This application will:

   1. Read public posts and comments from standing desk related
      subreddits (e.g., r/StandingDesk, r/Workspaces) to gather
      user opinions and experiences.

   2. Analyze product mentions, user reviews, and recommendations
      to help consumers make informed purchasing decisions.

   3. Retrieve publicly available information only - no posting,
      voting, or user interaction.

   4. Respect Reddit's API rate limits and terms of service.

   The app is for personal research purposes to understand real
   user experiences with standing desk products before making
   a purchase.
   ```

   **方案 2 - 简洁版**:
   ```
   The app will read public posts and comments from standing desk
   related subreddits (like r/StandingDesk) to analyze user opinions
   and product recommendations. It will only retrieve publicly
   available information and will not post, comment, or vote.
   The purpose is personal research to make an informed purchasing
   decision.
   ```

   **方案 3 - 学术研究版**:
   ```
   This research application will:

   1. Collect publicly available posts and comments from standing
      desk related subreddits for academic analysis.

   2. Analyze consumer sentiment, product preferences, and purchasing
      patterns to understand market trends.

   3. Only read public data - no posting, commenting, voting, or
      messaging.

   4. Follow all Reddit API guidelines and rate limits.

   5. Data will be used solely for research purposes and will not
      be shared or sold.
   ```

5. **提交创建**
   - 点击 "Create app" 按钮

---

### 第 3 步: 获取 API 凭证

创建成功后，你会看到应用详情：

```
DeepResearch Bot
personal use script

client_id: ABC123xyz456  ← 这是你的 Client ID（14 个字符）
secret: XYZ789abc123def456ghi789  ← 这是你的 Client Secret（27 个字符）
```

**重要**:
- `client_id` 在应用名称下方（小字）
- `secret` 在 "secret" 标签后面
- 请妥善保管这些凭证，不要泄露！

---

## 🔧 配置到 DeepResearch

### 方式 1: 环境变量配置（推荐）

编辑 `backend/.env` 文件，添加以下配置：

```bash
# Reddit API 配置
REDDIT_CLIENT_ID=ABC123xyz456
REDDIT_CLIENT_SECRET=XYZ789abc123def456ghi789
REDDIT_USER_AGENT=DeepResearch/1.0 by YourRedditUsername
```

**说明**:
- `REDDIT_CLIENT_ID`: 你的 Client ID
- `REDDIT_CLIENT_SECRET`: 你的 Client Secret
- `REDDIT_USER_AGENT`: 用户代理字符串（格式: `AppName/Version by RedditUsername`）

---

### 方式 2: 代码配置

如果不想使用环境变量，可以直接在代码中配置。

编辑 `backend/mcp_servers/content/scrapers/reddit.py`:

```python
import praw

class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id="ABC123xyz456",
            client_secret="XYZ789abc123def456ghi789",
            user_agent="DeepResearch/1.0 by YourRedditUsername"
        )
```

**注意**: 不推荐这种方式，因为凭证会暴露在代码中。

---

## 📦 安装 PRAW 库

Reddit 官方推荐使用 PRAW (Python Reddit API Wrapper) 库。

### 安装

```bash
cd backend
source .venv/bin/activate
pip install praw
```

### 更新 requirements.txt

```bash
echo "praw>=7.7.1" >> requirements.txt
```

---

## 🔄 更新代码以使用 Reddit API

### 1. 更新 Reddit Scraper

编辑 `backend/mcp_servers/content/scrapers/reddit.py`:

```python
import os
import praw
from typing import List, Dict, Any, Optional
from loguru import logger

class RedditScraper:
    def __init__(self):
        # 尝试使用 PRAW（需要 API 凭证）
        self.use_praw = self._init_praw()
        
        if not self.use_praw:
            logger.warning("Reddit API credentials not found, using JSON API")
    
    def _init_praw(self) -> bool:
        """初始化 PRAW，如果凭证可用"""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "DeepResearch/1.0")
        
        if client_id and client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                logger.info("✅ Reddit API initialized with PRAW")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize PRAW: {e}")
                return False
        return False
    
    async def get_subreddit_posts(
        self, 
        subreddit: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取子版块帖子"""
        if self.use_praw:
            return await self._get_posts_praw(subreddit, limit)
        else:
            return await self._get_posts_json(subreddit, limit)
    
    async def _get_posts_praw(
        self, 
        subreddit: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """使用 PRAW 获取帖子"""
        posts = []
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            for submission in subreddit_obj.hot(limit=limit):
                posts.append({
                    "title": submission.title,
                    "url": f"https://reddit.com{submission.permalink}",
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "created_utc": submission.created_utc,
                    "selftext": submission.selftext,
                    "author": str(submission.author),
                })
        except Exception as e:
            logger.error(f"PRAW error: {e}")
        return posts
    
    async def _get_posts_json(
        self, 
        subreddit: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """使用 JSON API 获取帖子（原有实现）"""
        # ... 保留原有的 JSON API 实现作为后备
        pass
```

---

## ✅ 测试配置

### 测试脚本

创建 `test_reddit_api.py`:

```python
import os
from dotenv import load_dotenv
import praw

load_dotenv("backend/.env")

def test_reddit_api():
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "DeepResearch/1.0")
    
    print(f"Client ID: {client_id[:5]}..." if client_id else "❌ Not found")
    print(f"Client Secret: {client_secret[:5]}..." if client_secret else "❌ Not found")
    print(f"User Agent: {user_agent}")
    
    if not client_id or not client_secret:
        print("\n❌ Reddit API credentials not configured")
        return
    
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # 测试获取子版块
        subreddit = reddit.subreddit("StandingDesk")
        print(f"\n✅ Connected to r/{subreddit.display_name}")
        print(f"Subscribers: {subreddit.subscribers:,}")
        
        # 测试获取帖子
        print("\n📝 Top 3 posts:")
        for i, post in enumerate(subreddit.hot(limit=3), 1):
            print(f"{i}. {post.title[:50]}... (Score: {post.score})")
        
        print("\n🎉 Reddit API test successful!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_reddit_api()
```

### 运行测试

```bash
cd /Users/ld/PyCharmMiscProject
source backend/.venv/bin/activate
python test_reddit_api.py
```

**预期输出**:
```
Client ID: ABC12...
Client Secret: XYZ78...
User Agent: DeepResearch/1.0 by YourUsername

✅ Connected to r/StandingDesk
Subscribers: 45,123

📝 Top 3 posts:
1. Best standing desk under $500? (Score: 234)
2. Uplift vs Jarvis comparison (Score: 189)
3. My DIY standing desk setup (Score: 156)

🎉 Reddit API test successful!
```

---

## 📊 API 限制

### 免费版限制

- **请求频率**: 60 次/分钟
- **每日请求**: 无限制（但受频率限制）
- **数据访问**: 公开内容

### 最佳实践

1. **使用缓存**: 避免重复请求相同内容
2. **限速**: 使用 RateLimiter 控制请求频率
3. **错误处理**: 优雅处理 API 错误
4. **后备方案**: 保留 JSON API 作为后备

---

## 🔍 常见问题

### Q1: 找不到 Client ID？

A: Client ID 在应用名称下方，是一串 14 个字符的字符串（如 `ABC123xyz456`）。

### Q2: 403 Forbidden 错误？

A: 检查：
- Client ID 和 Secret 是否正确
- User Agent 是否设置
- 是否超过请求限额

### Q3: 需要付费吗？

A: 不需要！Reddit API 对个人开发者免费。

### Q4: 可以不配置 API 吗？

A: 可以！DeepResearch 会自动降级到 JSON API（无需认证），但可能遇到 403 错误。

---

## 📚 参考资料

- [Reddit API 文档](https://www.reddit.com/dev/api/)
- [PRAW 文档](https://praw.readthedocs.io/)
- [Reddit App 管理](https://www.reddit.com/prefs/apps)

---

## ✨ 总结

**申请步骤**:
1. 创建 Reddit 账号
2. 创建 Reddit App（选择 "script" 类型）
3. 获取 Client ID 和 Secret

**配置步骤**:
1. 安装 PRAW: `pip install praw`
2. 配置环境变量（`backend/.env`）
3. 运行测试脚本验证

**优势**:
- ✅ 更高的请求限额
- ✅ 更稳定的服务
- ✅ 访问更多内容

---

**预计时间**: 10-15 分钟  
**难度**: ⭐⭐ (中等)  
**状态**: 可选配置（不配置也能使用）

