# Reddit API 快速参考

> **快速配置指南** - 5 分钟搞定

---

## 🚀 快速开始

### 1. 创建应用（3 分钟）

访问: https://www.reddit.com/prefs/apps

```
Name: DeepResearch Bot
Type: script ← 重要！
Description: Personal research tool for analyzing standing desk discussions
Redirect URI: http://localhost:8080
```

**可能的问题**:

Q: What benefit/purpose will the bot/app have for Redditors?
```
This app helps analyze product discussions and reviews on Reddit
to provide better product recommendations for consumers researching
standing desks.
```

Q: Provide a detailed description of what the Bot/App will be doing on the Reddit platform.
```
The app will read public posts and comments from standing desk
related subreddits (like r/StandingDesk) to analyze user opinions
and product recommendations. It will only retrieve publicly
available information and will not post, comment, or vote.
The purpose is personal research to make an informed purchasing
decision.
```

### 2. 获取凭证

创建后会看到：

```
DeepResearch Bot
personal use script

ABC123xyz456  ← 这是 Client ID（14 字符）
secret: XYZ789abc123def456ghi789  ← 这是 Secret（27 字符）
```

### 3. 配置环境变量

编辑 `backend/.env`:

```bash
REDDIT_CLIENT_ID=ABC123xyz456
REDDIT_CLIENT_SECRET=XYZ789abc123def456ghi789
REDDIT_USER_AGENT=DeepResearch/1.0 by YourRedditUsername
```

### 4. 安装依赖

```bash
cd backend
source .venv/bin/activate
pip install praw
```

### 5. 测试

```bash
python test_reddit_api.py
```

---

## 📊 对比

| 特性 | JSON API (无认证) | Reddit API (PRAW) |
|-----|------------------|-------------------|
| 请求限额 | 严格限制 | 60 次/分钟 |
| 稳定性 | ⚠️ 可能 403 | ✅ 稳定 |
| 配置难度 | 无需配置 | 5 分钟 |
| 推荐度 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🔍 常见问题

**Q: 必须配置吗？**  
A: 不必须，但强烈推荐。不配置可能遇到 403 错误。

**Q: 需要付费吗？**  
A: 不需要，完全免费。

**Q: Client ID 在哪里？**  
A: 在应用名称下方，14 个字符的字符串。

**Q: 配置后如何验证？**  
A: 运行 `python test_reddit_api.py`

---

## 📚 详细文档

完整教程: [docs/REDDIT_API_SETUP.md](REDDIT_API_SETUP.md)

---

**预计时间**: 5 分钟  
**难度**: ⭐⭐ (简单)  
**推荐**: ⭐⭐⭐⭐⭐

