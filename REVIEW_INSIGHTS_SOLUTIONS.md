# 评论洞察功能实现方案

> **更新时间**: 2026-01-14  
> **目标**: 实现主题聚类、情感分析、典型语句提取  
> **状态**: 🔍 方案对比

---

## 🎯 需求回顾

### 原始需求
1. **主题聚类/标签分布** - 10-20个标签
2. **Top正/负面要点** - 提取关键优缺点
3. **典型语句摘要** - 代表性评论

---

## 📊 方案对比

### 🥇 方案 1: LLM 直接分析（推荐）

**技术栈**:
- OpenAI GPT-4 / Claude / Gemini
- 一次性分析所有评论

**优点**:
- ✅ **最简单** - 一个 API 调用搞定
- ✅ **质量最高** - 理解上下文，提取准确
- ✅ **灵活** - 可以自定义输出格式
- ✅ **无需训练** - 开箱即用
- ✅ **多语言支持** - 自动处理

**缺点**:
- ⚠️ **成本** - 每次分析需要调用 API（但评论数量不多，成本可控）
- ⚠️ **Token 限制** - 需要分批处理大量评论

**实现示例**:
```python
prompt = f"""
分析以下产品评论，提取：
1. 主题标签（10-20个）- 格式：标签名 (出现次数)
2. Top 5 正面要点 - 附典型语句
3. Top 5 负面要点 - 附典型语句

评论列表：
{reviews}

输出 JSON 格式。
"""

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
```

**成本估算**:
- 100条评论 ≈ 20,000 tokens
- GPT-4: $0.03/1K tokens = $0.60/次
- Claude: $0.015/1K tokens = $0.30/次
- **每次分析成本 < $1**

**推荐度**: 🥇 **强烈推荐**

---

### 🥈 方案 2: BERTopic + Sentiment Analysis

**技术栈**:
- BERTopic (主题建模)
- Transformers (情感分析)
- BERT/RoBERTa embeddings

**优点**:
- ✅ **无 API 成本** - 本地运行
- ✅ **准确度高** - 基于 BERT embeddings
- ✅ **可视化** - BERTopic 提供主题可视化

**缺点**:
- ❌ **复杂** - 需要安装多个库
- ❌ **慢** - 本地计算耗时
- ❌ **需要调参** - 主题数量、聚类参数
- ❌ **依赖多** - transformers, bertopic, umap, hdbscan

**实现示例**:
```python
from bertopic import BERTopic
from transformers import pipeline

# 主题建模
topic_model = BERTopic(nr_topics=15)
topics, probs = topic_model.fit_transform(reviews)

# 情感分析
sentiment_pipeline = pipeline("sentiment-analysis")
sentiments = sentiment_pipeline(reviews)
```

**依赖**:
```
bertopic>=0.16.0
transformers>=4.30.0
torch>=2.0.0
umap-learn>=0.5.3
hdbscan>=0.8.33
```

**推荐度**: 🥈 备选方案（如果不想用 LLM）

---

### 🥉 方案 3: 传统 NLP (LDA + VADER)

**技术栈**:
- LDA (Latent Dirichlet Allocation) - 主题建模
- VADER - 情感分析
- TF-IDF - 关键词提取

**优点**:
- ✅ **最轻量** - 依赖少
- ✅ **最快** - 计算简单
- ✅ **稳定** - 成熟技术

**缺点**:
- ❌ **准确度低** - 无法理解上下文
- ❌ **需要预处理** - 分词、停用词、词干化
- ❌ **英文限定** - VADER 只支持英文

**实现示例**:
```python
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# LDA 主题建模
vectorizer = CountVectorizer(max_features=1000)
doc_term_matrix = vectorizer.fit_transform(reviews)
lda = LatentDirichletAllocation(n_components=15)
lda.fit(doc_term_matrix)

# VADER 情感分析
analyzer = SentimentIntensityAnalyzer()
sentiments = [analyzer.polarity_scores(r) for r in reviews]
```

**推荐度**: ⚠️ 不推荐（准确度太低）

---

### 🚀 方案 4: 混合方案（LLM + 缓存）

**技术栈**:
- LLM (主分析)
- Redis/SQLite (缓存结果)
- 增量分析

**优点**:
- ✅ **质量最高** - LLM 分析
- ✅ **成本可控** - 缓存结果，避免重复分析
- ✅ **快速** - 缓存命中直接返回

**实现逻辑**:
```python
async def analyze_reviews(reviews):
    # 1. 生成缓存 key（基于评论内容 hash）
    cache_key = hashlib.md5(json.dumps(reviews).encode()).hexdigest()
    
    # 2. 检查缓存
    cached = await cache.get(f"review_analysis:{cache_key}")
    if cached:
        return cached
    
    # 3. LLM 分析
    analysis = await llm_analyze(reviews)
    
    # 4. 缓存结果（7天）
    await cache.set(f"review_analysis:{cache_key}", analysis, ttl=7*24*3600)
    
    return analysis
```

**推荐度**: 🥇 **最佳方案**（LLM + 缓存）

---

## 🎯 最终推荐方案

### **方案 4: LLM + 缓存**

**理由**:
1. ✅ **质量最高** - LLM 理解上下文，提取准确
2. ✅ **实现简单** - 一个 Prompt 搞定
3. ✅ **成本可控** - 缓存机制，避免重复分析
4. ✅ **灵活** - 可以随时调整输出格式
5. ✅ **已有基础设施** - 项目已有 LLM 和缓存

**实现步骤**:
1. 使用现有的 `LLMService`
2. 设计 Prompt（主题聚类 + 情感分析 + 典型语句）
3. 使用现有的 `CacheManager`（7天缓存）
4. 返回结构化 JSON

---

## 📝 输出格式设计

```json
{
  "topics": [
    {
      "name": "稳定性",
      "count": 45,
      "percentage": 22.5,
      "sentiment": "mixed",
      "keywords": ["stable", "wobble", "sturdy"]
    },
    {
      "name": "价格",
      "count": 38,
      "percentage": 19.0,
      "sentiment": "negative",
      "keywords": ["expensive", "price", "cost"]
    }
  ],
  "positive_insights": [
    {
      "topic": "稳定性",
      "summary": "桌面非常稳定，即使升到最高也不晃动",
      "count": 32,
      "examples": [
        "Very stable even at max height",
        "No wobbling at all, very sturdy"
      ]
    }
  ],
  "negative_insights": [
    {
      "topic": "价格",
      "summary": "价格偏高，性价比不足",
      "count": 28,
      "examples": [
        "Too expensive for what you get",
        "Overpriced compared to competitors"
      ]
    }
  ],
  "sentiment_distribution": {
    "positive": 120,
    "neutral": 50,
    "negative": 30,
    "positive_percentage": 60.0,
    "negative_percentage": 15.0
  }
}
```

---

## 🚀 实施计划

### 阶段 1: 实现 Trustpilot Scraper（今天）
- [x] 创建 `TrustpilotReviewScraper`
- [x] 抓取评论数据
- [x] 注册到 Review MCP Server

### 阶段 2: 实现 LLM 评论分析（今天）
- [ ] 设计分析 Prompt
- [ ] 实现 `_analyze_reviews_with_llm()` 方法
- [ ] 添加缓存机制
- [ ] 更新 Orchestrator 调用

### 阶段 3: 更新前端显示（今天）
- [ ] 显示主题标签（标签云）
- [ ] 显示正/负面洞察
- [ ] 显示典型语句

---

## 💡 Prompt 设计（初稿）

```
你是一个专业的产品评论分析师。请分析以下 {brand} 产品的用户评论。

任务：
1. 提取 10-20 个主题标签（如：稳定性、价格、客服、组装难度等）
2. 统计每个主题的出现次数和情感倾向
3. 提取 Top 5 正面要点，附典型语句
4. 提取 Top 5 负面要点，附典型语句
5. 统计整体情感分布

评论列表（共 {count} 条）：
{reviews}

输出 JSON 格式，严格遵循以下结构：
{
  "topics": [...],
  "positive_insights": [...],
  "negative_insights": [...],
  "sentiment_distribution": {...}
}
```

---

## 📊 成本估算

### 假设
- 每个品牌 100 条评论
- 每条评论 100 tokens
- 总计 10,000 tokens/品牌

### 成本（使用 Claude）
- Input: 10,000 tokens × $0.003/1K = $0.03
- Output: 2,000 tokens × $0.015/1K = $0.03
- **总计: $0.06/品牌**

### 缓存效果
- 7天内重复查询：0 成本
- 每月分析 100 次：$6/月

**结论**: 成本完全可控！

---

## 🎯 总结

**最佳方案**: LLM + 缓存
- ✅ 质量最高
- ✅ 实现最简单
- ✅ 成本可控（$0.06/品牌）
- ✅ 灵活可调整

**下一步**: 立即实现！

