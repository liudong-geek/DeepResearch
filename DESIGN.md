# DeepResearch 竞品调研智能体 - 技术方案设计

> **项目目标**: 为 FlexiSpot 升降桌开品前调研，构建基于 MCP 的可追溯、结构化、自动化竞品调研系统

## 📋 需求概述

### 核心场景
为 FlexiSpot 独立站"升降桌"精品开品前，开发一个"竞品调研智能体工具"，自动输出：
- 市场机会信号
- 竞品对比
- 用户评价洞察
- 行动建议（运营/内容/投放/产品/客服）

### 输入参数
- **产品关键词**: standing desk（固定）
- **目标市场**: US（固定）
- **竞品列表**: 至少3个（Uplift / Jarvis / Vari / Autonomous 等）
- **数据来源**: 公开网页（遵守 robots.txt，限速抓取）

### 输出要求
1. **证据引用**: 每个结论可追溯到来源 URL + 引用片段
2. **竞品对比表**: 价格带、卖点、痛点、交付/售后、材质/稳定性
3. **评论洞察**: 主题聚类（10-20个标签）、正/负面要点、典型语句
4. **行动计划**: 运营/投放/产品/客服建议
5. **效率证明**: 人工 vs 工具耗时对比

### 必须交付
- ✅ 可访问的前端界面（输入→运行→展示报告）
- ✅ 完整 Repo（README、一键运行、.env.example）
- ✅ 爬虫模块（限速/重试/去重/缓存/增量）
- ✅ 智能体/工作流实现
- ✅ 3-5分钟演示录屏

---

## 🎯 MCP 架构核心价值

### 为什么选择 MCP？
1. ✅ **标准化工具接口**: 爬虫能力作为 Tools 暴露给 LLM
2. ✅ **解耦数据获取与编排**: MCP Server 专注数据采集，Client 专注业务逻辑
3. ✅ **可组合性**: 多个垂直 MCP Server 可独立开发、测试、复用
4. ✅ **简化智能体编排**: LLM 直接调用 MCP Tools，减少复杂 workflow 代码

### 智能体编排简化程度
- ❌ **不能完全省略**: 仍需任务分解、结果聚合、报告生成逻辑
- ✅ **可大幅简化**: 从复杂的 LangGraph/CrewAI 多 Agent 协作 → 单 Agent + MCP Tools 调用
- ✅ **推荐方案**: **轻量级编排层**（简单 Python 脚本 + LLM Function Calling）

---

## 🏗️ 系统架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      前端展示层 (Next.js)                    │
│  - 输入表单 (关键词/市场/竞品列表)                           │
│  - 报告展示 (表格/图表/引用溯源)                             │
│  - 实时进度 (WebSocket/SSE)                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP API
┌──────────────────────▼──────────────────────────────────────┐
│              智能体编排层 (FastAPI Backend)                  │
│  - 任务分解 (Task Planner)                                   │
│  - LLM 调用 (OpenAI/Claude + Function Calling)               │
│  - 结果聚合 (Report Generator)                               │
│  - 缓存管理 (Redis/SQLite)                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ MCP Protocol
┌──────────────────────▼──────────────────────────────────────┐
│                   MCP Server 集群                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │ E-commerce MCP │  │ Review MCP     │  │ Content MCP    ││
│  │ - 产品页抓取   │  │ - Amazon评论   │  │ - Reddit/论坛  ││
│  │ - 价格/规格    │  │ - Trustpilot   │  │ - 测评文章     ││
│  │ - 库存/SKU     │  │ - 情感分析     │  │ - YouTube评论  ││
│  └────────────────┘  └────────────────┘  └────────────────┘│
│  ┌────────────────┐  ┌────────────────┐                     │
│  │ SEO/Ads MCP    │  │ Social MCP     │                     │
│  │ - Google搜索   │  │ - Twitter/X    │                     │
│  │ - 广告文案     │  │ - Facebook群组 │                     │
│  └────────────────┘  └────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              数据存储层 (PostgreSQL + Vector DB)             │
│  - 原始数据 (URL/HTML/JSON)                                  │
│  - 结构化数据 (产品/评论/文章)                               │
│  - 向量索引 (语义搜索/去重)                                  │
│  - 引用关系 (结论→证据映射)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 MCP Server 垂直领域划分

### 1️⃣ E-commerce MCP Server（电商产品数据）
**职责**: 抓取竞品官网产品页

**Tools**:
- `get_product_info(url)` → 产品名称、价格、规格、图片
- `get_product_specs(url)` → 详细参数表
- `search_products(brand, keyword)` → 产品列表

**数据源**:
- FlexiSpot, Uplift, Jarvis, Vari, Autonomous 官网
- 限速策略: 每域名 1 req/2s
- 缓存: 7天

**技术实现**:
- 静态页面: `httpx` + `BeautifulSoup`
- 动态页面: `playwright` 无头浏览器

---

### 2️⃣ Review MCP Server（用户评论数据）
**职责**: 抓取多平台评论并分析

**Tools**:
- `get_amazon_reviews(asin, max_count)` → 评论列表
- `get_trustpilot_reviews(company)` → 评论列表
- `analyze_sentiment(reviews)` → 情感分布
- `extract_topics(reviews)` → 主题标签

**数据源**:
- Amazon（通过 API 或 Scraper API）
- Trustpilot
- Reddit (r/StandingDesk)
- 限速策略: 每平台 1 req/3s
- 去重: 基于评论内容 hash

**分析能力**:
- 情感分析: 正面/负面/中性分类
- 主题提取: LDA/BERTopic 聚类
- 关键词提取: TF-IDF + 词频统计

---

### 3️⃣ Content MCP Server（测评内容）
**职责**: 抓取测评文章、视频

**Tools**:
- `search_reviews(keyword, site)` → 文章列表
- `extract_article_content(url)` → 正文+评分
- `get_youtube_comments(video_id)` → 视频评论

**数据源**:
- Wirecutter, RTINGS, PCMag 等测评网站
- YouTube
- 限速策略: 每站点 1 req/5s

        # 2. 并行执行 MCP 工具调用
        results = await asyncio.gather(*[
            self.execute_tool(tool_call)
            for tool_call in plan.tool_calls
        ])

        # 3. 结果聚合（LLM 生成结构化报告）
        report = await self.llm.generate_report(
            raw_data=results,
            template=REPORT_TEMPLATE
        )

        # 4. 引用溯源（建立结论→证据映射）
        report_with_citations = self.add_citations(report, results)

        return report_with_citations
```

### 为什么可以简化？

| 传统多 Agent 方案 | MCP + 单 Agent 方案 |
|------------------|---------------------|
| 需要定义多个 Agent 角色 | 只需 1 个 Orchestrator |
| Agent 间通信协议复杂 | LLM 直接调用 MCP Tools |
| 状态管理复杂 | 无状态工具调用 |
| 调试困难 | 工具调用可追踪 |

---

## 📊 数据流与引用溯源设计

### 引用溯源数据结构

```json
{
  "conclusion": "Uplift 的稳定性评价优于 FlexiSpot",
  "confidence": 0.85,
  "evidence": [
    {
      "source_type": "review",
      "url": "https://amazon.com/...",
      "snippet": "The Uplift desk is rock solid, no wobble at all",
      "timestamp": "2024-01-15",
      "relevance_score": 0.92
    },
    {
      "source_type": "article",
      "url": "https://wirecutter.com/...",
      "snippet": "In our stability tests, Uplift scored 9/10 vs FlexiSpot's 7/10",
      "timestamp": "2023-12-01",
      "relevance_score": 0.88
    }
  ]
}
```

### 实现方式
1. **MCP Server 返回时携带元数据**: 每个数据点包含 `source_url`, `extracted_at`, `raw_html_hash`
2. **向量数据库存储**: 原始数据 + Embedding，支持语义去重
3. **前端点击引用**: 跳转到原始 URL + 高亮引用片段

### 溯源保障机制
- **三层保障**:
  1. MCP Server 返回时强制携带 `source_url` + `timestamp`
  2. 数据库存储原始 HTML（hash 去重）
  3. 前端展示时验证链接有效性

---

## 🎨 前端设计要点

### 技术栈推荐
- **框架**: Next.js 14 (App Router)
- **UI**: Tailwind CSS + shadcn/ui
- **图表**: Recharts / Chart.js
- **状态管理**: Zustand / React Query
- **实时通信**: WebSocket / Server-Sent Events

### 核心页面

#### 1. 输入页
- 关键词: `standing desk`（固定）
- 市场: `US`（固定）
- 竞品选择: 多选框（Uplift, Jarvis, Vari, Autonomous, 自定义）
- 开始调研按钮

#### 2. 进度页
- 实时显示: 正在抓取 XX 网站...
- 进度条: 已完成 X/Y 个任务
- WebSocket 推送更新

#### 3. 报告页

**Tab 1: 竞品对比表**
- 表格: 价格/卖点/痛点/材质/稳定性
- 每个单元格右上角有 `[引用]` 图标，点击展开证据

**Tab 2: 评论洞察**
- 标签云: Top 20 主题标签
- 正面/负面 Top 5 要点
- 典型评论摘录（带来源链接）

**Tab 3: 行动计划**
- 运营建议（上新策略/定价带/PDP结构）
- 投放建议（受众假设/素材方向/文案方向）
- 产品改进 Top 5
- 客服 FAQ

**Tab 4: 效率对比**
- 人工调研 vs 工具调研耗时对比图

### 引用组件设计

```tsx
// CitationPopover 组件示例
<CitationPopover>
  <Trigger>
    <sup className="citation-link">[1]</sup>
  </Trigger>
  <Content>
    <div className="citation-card">
      <p className="snippet">"The Uplift desk is rock solid..."</p>
      <a href={url} target="_blank">查看原文 →</a>
      <span className="timestamp">2024-01-15</span>
    </div>
  </Content>
</CitationPopover>
```

---

## 🛠️ 技术栈详细说明

### 后端技术栈
- **语言**: Python 3.11+
- **框架**: FastAPI
- **MCP SDK**: `mcp`（官方 Python SDK）
- **爬虫**:
  - `httpx`（HTTP 客户端）
  - `playwright`（动态页面）
  - `beautifulsoup4`（HTML 解析）
- **限速**: `aiolimiter`
- **缓存**: Redis / SQLite
- **数据库**: PostgreSQL + pgvector（向量搜索）
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **异步**: `asyncio` + `aiohttp`

### 前端技术栈
- **框架**: Next.js 14
- **语言**: TypeScript
- **UI**: Tailwind CSS + shadcn/ui
- **请求**: React Query
- **图表**: Recharts
- **状态**: Zustand

### 基础设施
- **容器化**: Docker Compose
- **部署**:
  - 前端: Vercel
  - 后端: Railway / Fly.io
- **监控**: Sentry（错误追踪）
- **日志**: Loguru

---

## 📁 项目结构

```
deep-research/
├── backend/
│   ├── mcp_servers/              # MCP Server 集群
│   │   ├── ecommerce/
│   │   │   ├── server.py         # E-commerce MCP Server
│   │   │   ├── scrapers/         # 各品牌爬虫
│   │   │   │   ├── uplift.py
│   │   │   │   ├── jarvis.py
│   │   │   │   └── base.py
│   │   │   └── tools.py          # MCP Tools 定义
│   │   ├── review/
│   │   │   ├── server.py
│   │   │   ├── scrapers/
│   │   │   │   ├── amazon.py
│   │   │   │   ├── trustpilot.py
│   │   │   │   └── reddit.py
│   │   │   └── tools.py
│   │   ├── content/
│   │   │   ├── server.py
│   │   │   ├── scrapers/
│   │   │   └── tools.py
│   │   ├── seo/
│   │   │   ├── server.py
│   │   │   └── tools.py
│   │   └── social/
│   │       ├── server.py
│   │       └── tools.py
│   ├── orchestrator/             # 智能体编排层
│   │   ├── agent.py              # 主编排逻辑
│   │   ├── llm_client.py         # LLM 调用封装
│   │   ├── report_generator.py  # 报告生成
│   │   └── prompts/              # Prompt 模板
│   ├── api/                      # FastAPI 接口
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── research.py
│   │   │   └── health.py
│   │   └── models/               # Pydantic 模型
│   ├── db/                       # 数据库模型
│   │   ├── models.py
│   │   └── migrations/
│   ├── cache/                    # 缓存层
│   │   ├── redis_client.py
│   │   └── strategies.py
│   ├── utils/                    # 工具函数
│   │   ├── rate_limiter.py
│   │   ├── retry.py
│   │   └── deduplication.py
│   ├── tests/                    # 测试
│   │   ├── test_mcp_servers/
│   │   └── test_orchestrator/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                      # Next.js App Router
│   │   ├── page.tsx              # 输入页
│   │   ├── research/
│   │   │   └── [id]/
│   │   │       └── page.tsx      # 报告页
│   │   ├── layout.tsx
│   │   └── api/                  # API Routes
│   │       └── research/
│   ├── components/
│   │   ├── ui/                   # shadcn/ui 组件
│   │   ├── ComparisonTable.tsx
│   │   ├── CitationPopover.tsx
│   │   ├── InsightsDashboard.tsx
│   │   ├── ProgressTracker.tsx
│   │   └── ActionPlan.tsx
│   ├── lib/
│   │   ├── api-client.ts
│   │   └── utils.ts
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
├── DESIGN.md                     # 本文档
└── docs/
    ├── API.md                    # API 文档
    ├── MCP_SERVERS.md            # MCP Server 开发指南
    └── DEPLOYMENT.md             # 部署指南
```

---

## 🚀 实施路线图

### Phase 1: MCP Server 开发（Week 1-2）
**目标**: 完成核心数据采集能力

- [ ] Day 1-2: 搭建 E-commerce MCP Server
  - [ ] Uplift 爬虫（产品页/规格）
  - [ ] Jarvis 爬虫
  - [ ] 限速/重试机制
- [ ] Day 3-4: 搭建 Review MCP Server
  - [ ] Amazon 评论抓取
  - [ ] 情感分析集成
  - [ ] 主题提取（BERTopic）
- [ ] Day 5-6: 搭建 Content MCP Server
  - [ ] Wirecutter 文章抓取
  - [ ] YouTube 评论抓取
- [ ] Day 7: 单元测试 + 集成测试
  - [ ] 每个 MCP Server 独立测试
  - [ ] 限速/缓存/去重验证

**交付物**:
- 3个可运行的 MCP Server
- 测试覆盖率 > 80%
- 技术文档

---

### Phase 2: 智能体编排（Week 2）
**目标**: 实现任务分解与报告生成

- [ ] Day 8-9: 实现 Orchestrator
  - [ ] MCP Client 集成
  - [ ] 任务分解逻辑
  - [ ] 并行调用管理
- [ ] Day 10: LLM Function Calling 集成
  - [ ] OpenAI/Claude API 封装
  - [ ] Prompt 工程
  - [ ] 错误处理
- [ ] Day 11-12: 报告生成
  - [ ] 竞品对比表生成
  - [ ] 评论洞察聚合
  - [ ] 行动计划生成
- [ ] Day 13-14: 引用溯源
  - [ ] 结论→证据映射
  - [ ] 数据库存储
  - [ ] 向量去重

**交付物**:
- 完整的后端 API
- 端到端测试（输入→输出）
- API 文档

---

### Phase 3: 前端开发（Week 3）
**目标**: 构建用户界面

- [ ] Day 15-16: Next.js 项目搭建
  - [ ] 项目初始化
  - [ ] shadcn/ui 集成
  - [ ] 路由设计
- [ ] Day 17: 输入表单 + 进度页
  - [ ] 竞品选择组件
  - [ ] WebSocket 实时进度
- [ ] Day 18-19: 报告展示
  - [ ] 竞品对比表组件
  - [ ] 评论洞察仪表盘
  - [ ] 引用弹窗组件
- [ ] Day 20-21: 行动计划 + 优化
  - [ ] 行动计划展示
  - [ ] 响应式设计
  - [ ] 性能优化

**交付物**:
- 完整的前端应用
- 响应式设计
- 用户体验优化

---

### Phase 4: 集成测试 & 优化（Week 4）
**目标**: 完善系统并准备交付

- [ ] Day 22-23: 端到端测试
  - [ ] 完整流程测试（3个竞品）
  - [ ] 边界情况测试
  - [ ] 性能测试
- [ ] Day 24: 性能优化
  - [ ] 缓存策略优化
  - [ ] 并发控制
  - [ ] 数据库查询优化
- [ ] Day 25-26: 文档完善
  - [ ] README 编写
  - [ ] 部署指南
  - [ ] API 文档
  - [ ] 一键运行脚本
- [ ] Day 27-28: 演示录屏
  - [ ] 录制 3-5 分钟演示
  - [ ] 准备演讲稿
  - [ ] 最终检查

**交付物**:
- 完整的可部署系统
- 完善的文档
- 演示视频

---

## 🔧 爬虫稳定性保障

### 限速策略
```python
# 每域名独立限速
from aiolimiter import AsyncLimiter

class RateLimitedScraper:
    def __init__(self):
        self.limiters = {
            'uplift.com': AsyncLimiter(1, 2),      # 1 req / 2s
            'amazon.com': AsyncLimiter(1, 3),      # 1 req / 3s
            'wirecutter.com': AsyncLimiter(1, 5),  # 1 req / 5s
        }

    async def fetch(self, url: str):
        domain = extract_domain(url)
        async with self.limiters[domain]:
            return await httpx.get(url)
```

### 重试机制
```python
# 指数退避重试
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def fetch_with_retry(url: str):
    response = await httpx.get(url)
    response.raise_for_status()
    return response
```

### 去重策略
1. **URL 去重**: 基于 URL hash（MD5）
2. **内容去重**: 基于内容 hash（SimHash）
3. **语义去重**: 基于 Embedding 相似度（> 0.95 视为重复）

### 缓存策略
```python
# Redis 缓存
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_or_fetch(self, url: str, ttl: int = 604800):  # 7天
        cache_key = f"scrape:{hash(url)}"
        cached = await self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        data = await fetch(url)
        await self.redis.setex(cache_key, ttl, json.dumps(data))
        return data
```

### 增量抓取
```python
# 记录上次抓取时间
class IncrementalScraper:
    async def scrape_reviews(self, product_id: str):
        last_scraped = await db.get_last_scrape_time(product_id)

        # 只抓取新评论
        reviews = await fetch_reviews_since(product_id, last_scraped)

        await db.update_last_scrape_time(product_id, datetime.now())
        return reviews
```

---

## 🎯 关键问题解答

### Q1: MCP 是否能完全替代智能体编排？
**A**: 不能完全替代，但可以大幅简化：
- **MCP 负责**: 数据获取能力标准化
- **编排层负责**: 任务分解、结果聚合、业务逻辑
- **推荐**: **单 Agent + MCP Tools** 而非多 Agent 协作

**对比**:
```
传统方案:
  Planner Agent → Data Agent → Analysis Agent → Report Agent
  (4个 Agent，复杂状态管理)

MCP 方案:
  Orchestrator + LLM Function Calling → MCP Tools
  (1个编排器，无状态工具调用)
```

---

### Q2: 如何保证引用溯源的可靠性？
**A**: 三层保障机制

1. **数据采集层**:
   - MCP Server 返回时强制携带元数据
   ```python
   {
     "data": "Uplift desk is stable",
     "metadata": {
       "source_url": "https://...",
       "extracted_at": "2024-01-15T10:30:00Z",
       "html_hash": "abc123..."
     }
   }
   ```

2. **存储层**:
   - 数据库存储原始 HTML（hash 去重）
   - 向量数据库存储 Embedding（语义搜索）
   ```sql
   CREATE TABLE evidence (
     id UUID PRIMARY KEY,
     source_url TEXT NOT NULL,
     content TEXT NOT NULL,
     html_raw TEXT,
     embedding VECTOR(1536),
     extracted_at TIMESTAMP
   );
   ```

3. **展示层**:
   - 前端验证链接有效性
   - 点击引用时高亮原文片段
   - 显示抓取时间戳

---

### Q3: 爬虫稳定性如何保证？
**A**: 五大机制

| 机制 | 实现 | 效果 |
|------|------|------|
| **限速** | `aiolimiter` 每域名独立限速 | 避免被封 IP |
| **重试** | 指数退避（1s → 2s → 4s） | 应对临时故障 |
| **去重** | URL hash + 内容 hash + Embedding | 节省资源 |
| **缓存** | Redis 7天 TTL | 减少重复抓取 |
| **增量** | 记录上次抓取时间 | 只抓新数据 |

**监控指标**:
- 成功率: > 95%
- 平均响应时间: < 3s
- 缓存命中率: > 60%

---

### Q4: 如何处理动态加载的页面？
**A**: 智能检测 + 分层处理

```python
async def smart_fetch(url: str):
    # 1. 先尝试静态抓取
    response = await httpx.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 2. 检测是否需要 JS 渲染
    if needs_js_rendering(soup):
        # 使用 Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            content = await page.content()
            await browser.close()
            return content

    return response.text

def needs_js_rendering(soup):
    # 检测特征
    indicators = [
        soup.find('div', id='root'),           # React
        soup.find('div', id='__next'),         # Next.js
        soup.find('script', text=re.compile('window.__INITIAL_STATE__'))
    ]
    return any(indicators)
```

---

### Q5: LLM 成本如何控制？
**A**: 三级优化

1. **Prompt 优化**:
   - 使用结构化输出（JSON Mode）
   - 减少不必要的上下文
   - 缓存常用 Prompt

2. **模型选择**:
   - 简单任务: GPT-3.5-turbo（$0.001/1K tokens）
   - 复杂分析: GPT-4-turbo（$0.01/1K tokens）
   - 情感分析: 本地模型（免费）

3. **缓存策略**:
   - 相同输入缓存结果
   - 预计成本: 100次调研 ≈ $30-50

---

## 📈 评分标准对应

| 评分项（100分） | 设计对应 | 实现要点 | 预期得分 |
|----------------|---------|---------|---------|
| **业务可用性（25）** | 结构化报告 + 行动建议 | - 竞品对比表<br>- 评论洞察<br>- 行动计划<br>- 效率对比 | 22-25 |
| **引用溯源（20）** | 三层溯源机制 + 前端引用组件 | - 元数据强制携带<br>- 数据库存储原文<br>- 前端引用弹窗 | 18-20 |
| **爬虫稳定性（20）** | 限速/重试/去重/缓存完整实现 | - 每域名独立限速<br>- 指数退避重试<br>- 三层去重<br>- Redis 缓存 | 18-20 |
| **前端体验（20）** | Next.js + 响应式 + 实时进度 | - shadcn/ui 组件<br>- WebSocket 进度<br>- 引用可点击 | 17-20 |
| **工程化（15）** | Docker + 文档 + 测试 | - Docker Compose<br>- README/API 文档<br>- 测试覆盖率 > 80% | 13-15 |
| **总计** | | | **88-100** |

---

## 💡 实施建议

### 优先级排序
1. **先做 MVP**（Week 1-2）:
   - E-commerce MCP（Uplift + Jarvis）
   - Review MCP（Amazon）
   - 基础前端（输入 + 简单报告）

2. **验证可行性**（Week 2）:
   - 跑通一个完整流程（1个竞品）
   - 验证引用溯源
   - 测试爬虫稳定性

3. **再扩展**（Week 3-4）:
   - 添加更多 MCP Server
   - 完善前端体验
   - 优化性能

### 技术选型建议
- ✅ **推荐 MCP**: 标准化、可复用、易测试
- ✅ **简化编排**: 单 Agent + Function Calling，避免过度设计
- ✅ **前端优先**: 报告展示是评分重点

### 风险提示
- ⚠️ **反爬虫**: 准备备用数据源（SerpAPI, ScraperAPI）
- ⚠️ **LLM 成本**: 预估 100次调研 ≈ $30-50（GPT-4）
- ⚠️ **时间压力**: 4周完成需要每天投入 4-6 小时
- ⚠️ **数据质量**: 部分网站可能无法抓取，需要降级方案

---

## 🎬 下一步行动

### 立即开始（今天）
1. ✅ 确认技术栈
2. ✅ 搭建项目骨架
3. ✅ 配置开发环境

### Day 1-3
- [ ] 开发 E-commerce MCP Server（Uplift 爬虫）
- [ ] 实现限速/重试/缓存
- [ ] 单元测试

### Day 4-5
- [ ] 开发 Review MCP Server（Amazon）
- [ ] 集成情感分析
- [ ] 测试去重机制

### Day 6-7
- [ ] 实现 Orchestrator
- [ ] LLM Function Calling 集成
- [ ] 端到端测试

### Day 8-10
- [ ] 前端开发（输入 + 报告）
- [ ] 引用组件
- [ ] WebSocket 进度

### Day 11-14
- [ ] 完善功能
- [ ] 性能优化
- [ ] 文档 + 演示录屏

---

## 📚 参考资源

### MCP 相关
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP 示例项目](https://github.com/modelcontextprotocol/servers)

### 爬虫技术
- [Playwright 文档](https://playwright.dev/python/)
- [httpx 文档](https://www.python-httpx.org/)
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/)

### LLM 集成
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Claude API](https://docs.anthropic.com/claude/docs)

### 前端技术
- [Next.js 14 文档](https://nextjs.org/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 📝 版本历史

- **v1.0** (2026-01-11): 初始设计方案
  - 完成架构设计
  - 定义 MCP Server 划分
  - 制定实施路线图

---

**文档维护**: 本文档将随项目进展持续更新
**最后更新**: 2026-01-11
**作者**: AI Assistant + 项目团队
**职责**: 分析竞品 SEO 和广告策略

**Tools**:
- `google_search(keyword, market)` → 搜索结果
- `get_serp_features(keyword)` → Featured Snippet/People Also Ask
- `analyze_ad_copy(brand)` → 广告文案分析

**数据源**:
- Google Search（通过 SerpAPI）
- Google Ads Library（如可访问）

---

### 5️⃣ Social MCP Server（社交媒体）
**职责**: 社交平台讨论分析

**Tools**:
- `search_reddit(subreddit, keyword)` → 帖子列表
- `get_twitter_mentions(brand)` → 推文列表

**数据源**:
- Reddit API
- Twitter/X API（需 API Key）

---

## 🤖 智能体编排层设计（简化版）

### 核心流程

```python
# 伪代码示例
class ResearchOrchestrator:
    def __init__(self, mcp_clients: List[MCPClient], llm: LLM):
        self.mcp_clients = mcp_clients
        self.llm = llm

    async def run_research(self, keyword: str, market: str, competitors: List[str]):
        # 1. 任务分解（LLM 生成调用计划）
        plan = await self.llm.create_research_plan(
            keyword=keyword,
            competitors=competitors,
            available_tools=self.get_all_mcp_tools()
        )

