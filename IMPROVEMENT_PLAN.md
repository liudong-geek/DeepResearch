# 🎯 DeepResearch 核心改进方案

## 📊 当前问题分析

### 1. 数据来源单一性 ❌ (严重)

**当前状态**:
- ✅ 竞品官网产品页（Uplift, Vari, Jarvis）
- ❌ 缺少评论数据（Amazon, Reddit, YouTube）
- ❌ 缺少测评文章（Wirecutter, RTINGS, YouTube）
- ❌ 缺少论坛讨论（Reddit, Quora）
- ❌ 缺少社交媒体（Twitter, Facebook）

**影响**:
- 业务可用性：15/25 分（只有产品信息，缺少用户真实反馈）
- 引用溯源：10/20 分（来源单一，不够全面）

### 2. 引用溯源不足 ❌ (严重)

**当前状态**:
- ❌ LLM 生成的结论没有明确的引用来源
- ❌ 无法追溯每个结论来自哪个数据源
- ❌ 前端没有显示引用链接

**影响**:
- 引用溯源：5/20 分（无法审计、无法追溯）
- 业务可用性：降低（决策者无法验证数据真实性）

### 3. 爬虫稳定性 ✅ (良好)

**当前状态**:
- ✅ 限速机制（Token Bucket, 0.5 req/s）
- ✅ 重试机制（指数退避，最多 3 次）
- ✅ 去重机制（URL 去重）
- ✅ 缓存机制（7 天 TTL）
- ⚠️  增量抓取（基础实现，可优化）

**评分**: 18/20 分

### 4. 前端体验 ⚠️  (中等)

**当前状态**:
- ✅ 实时进度条
- ✅ 结构化展示
- ⚠️  缺少引用链接
- ⚠️  缺少数据来源标注
- ❌ 缺少 SEO 优化

**评分**: 12/20 分

---

## 🎯 改进方案（按优先级）

### Phase 1: 扩展数据来源（核心）

#### 1.1 Amazon 评论抓取 🔥
**优先级**: P0（最高）

**实现**:
```python
# backend/mcp_servers/review/scrapers/amazon.py
class AmazonReviewScraper:
    async def scrape_reviews(self, asin: str, limit: int = 100):
        """抓取 Amazon 评论"""
        # 1. 搜索产品 ASIN
        # 2. 抓取评论列表
        # 3. 提取：评分、标题、内容、日期、验证购买
        # 4. 返回结构化数据
```

**数据源**:
- Amazon 产品评论页
- 筛选：验证购买、最有帮助、最新

**价值**:
- 真实用户反馈
- 痛点和需求洞察
- 竞品优缺点

#### 1.2 Reddit 讨论抓取 🔥
**优先级**: P0

**实现**:
```python
# backend/mcp_servers/content/scrapers/reddit.py
class RedditScraper:
    async def search_discussions(self, keyword: str, subreddits: List[str]):
        """搜索 Reddit 讨论"""
        # Subreddits: r/StandingDesk, r/HomeOffice, r/Ergonomics
        # 提取：标题、内容、评论、投票数
```

**数据源**:
- r/StandingDesk
- r/HomeOffice
- r/Ergonomics
- r/BuyItForLife

**价值**:
- 用户真实讨论
- 品牌口碑
- 常见问题

#### 1.3 测评文章抓取 🔥
**优先级**: P1

**实现**:
```python
# backend/mcp_servers/content/scrapers/review_sites.py
class ReviewSiteScraper:
    async def scrape_review_article(self, url: str):
        """抓取测评文章"""
        # 网站：Wirecutter, RTINGS, TechRadar
        # 提取：评分、优缺点、推荐理由
```

**数据源**:
- Wirecutter (NYTimes)
- RTINGS
- TechRadar
- PCMag

**价值**:
- 专业评测
- 详细对比
- 权威推荐

#### 1.4 YouTube 视频分析
**优先级**: P2

**实现**:
```python
# backend/mcp_servers/content/scrapers/youtube.py
class YouTubeScraper:
    async def get_video_transcript(self, video_id: str):
        """获取视频字幕"""
        # 使用 YouTube API 或 youtube-transcript-api
        # 提取：字幕、评论、点赞数
```

**数据源**:
- 开箱视频
- 对比测评
- 用户评价

---

### Phase 2: 引用溯源系统

#### 2.1 数据结构改进

**当前**:
```json
{
  "price_comparison": {
    "Uplift": {"price": 299.99, "positioning": "中端"}
  }
}
```

**改进后**:
```json
{
  "price_comparison": {
    "Uplift": {
      "price": 299.99,
      "positioning": "中端",
      "sources": [
        {
          "type": "product_page",
          "url": "https://www.upliftdesk.com/...",
          "extracted_at": "2026-01-12T21:30:00Z",
          "data_point": "price"
        }
      ]
    }
  }
}
```

#### 2.2 LLM Prompt 改进

```python
prompt = f"""
请分析以下数据并生成报告。

**重要**: 每个结论必须标注数据来源！

输出格式:
{{
  "conclusion": "结论内容",
  "sources": [
    {{"type": "amazon_review", "url": "...", "quote": "原文引用"}},
    {{"type": "reddit_post", "url": "...", "quote": "原文引用"}}
  ],
  "confidence": 0.85
}}
```

#### 2.3 前端展示改进

```tsx
<div className="conclusion">
  <p>{conclusion.text}</p>
  <div className="sources">
    <h4>数据来源:</h4>
    {conclusion.sources.map(source => (
      <a href={source.url} target="_blank">
        [{source.type}] {source.quote}
      </a>
    ))}
  </div>
</div>
```

---

### Phase 3: 前端体验优化

#### 3.1 引用链接展示
- 每个数据点添加 [来源] 标签
- 点击可查看原始数据
- 显示抓取时间

#### 3.2 数据可信度指标
- 显示数据来源数量
- 显示数据新鲜度
- 显示置信度评分

#### 3.3 SEO 优化
- 添加 meta 标签
- 结构化数据（JSON-LD）
- 语义化 HTML

---

## 📈 预期评分提升

| 维度 | 当前 | 改进后 | 提升 |
|------|------|--------|------|
| 业务可用性 | 15/25 | 23/25 | +8 |
| 引用溯源 | 5/20 | 18/20 | +13 |
| 爬虫稳定性 | 18/20 | 20/20 | +2 |
| 前端体验 | 12/20 | 18/20 | +6 |
| **总分** | **50/85** | **79/85** | **+29** |

---

## 🚀 实施计划

### Week 1: 数据来源扩展
- [ ] Day 1-2: Amazon 评论爬虫
- [ ] Day 3-4: Reddit 讨论爬虫
- [ ] Day 5: 测评文章爬虫

### Week 2: 引用溯源系统
- [ ] Day 1-2: 数据结构改进
- [ ] Day 3-4: LLM Prompt 优化
- [ ] Day 5: 前端引用展示

### Week 3: 体验优化
- [ ] Day 1-2: 前端 UI 改进
- [ ] Day 3-4: SEO 优化
- [ ] Day 5: 测试和优化

---

## 💡 立即可做的快速改进

1. **添加数据来源标注** (1 小时)
   - 在前端显示每个数据的来源 URL
   
2. **改进 LLM Prompt** (30 分钟)
   - 要求 LLM 返回引用来源

3. **添加置信度评分** (1 小时)
   - 根据数据来源数量计算置信度

4. **优化前端展示** (2 小时)
   - 添加"数据来源"区块
   - 显示抓取时间和来源链接

