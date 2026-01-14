# 评论洞察溯源功能

## 📋 功能说明

为评论洞察部分添加了数据溯源链接，用户可以点击链接查看原始评论来源。

## ✅ 后端修改

### 文件: `backend/orchestrator/orchestrator.py`

在 `_analyze_reviews()` 方法中添加了溯源信息：

```python
# 添加溯源信息
sources = []
for brand_reviews in review_data:
    if '_source' in brand_reviews:
        sources.append({
            'type': brand_reviews['_source']['type'],
            'brand': brand_reviews['_source']['brand'],
            'url': brand_reviews['_source']['url'],
            'review_count': len(brand_reviews.get('reviews', [])),
            'overall_rating': brand_reviews.get('overall_rating', 0)
        })

# 如果有 Reddit 数据，也添加溯源
if reddit_data:
    for post in reddit_data:
        if '_source' in post:
            sources.append({
                'type': 'reddit_discussion',
                'url': post['_source'].get('url', ''),
                'title': post.get('title', ''),
                'score': post.get('score', 0)
            })

# 将溯源信息添加到分析结果中
analysis['_sources'] = sources
analysis['_metadata'] = {
    'total_reviews_analyzed': sum(len(br.get('reviews', [])) for br in review_data),
    'total_reddit_posts': len(reddit_data) if reddit_data else 0,
    'brands_analyzed': [s['brand'] for s in sources if s['type'] == 'trustpilot_reviews']
}
```

### 返回数据结构

```json
{
  "topics": [...],
  "sentiment_distribution": {...},
  "positive_insights": [...],
  "negative_insights": [...],
  "_sources": [
    {
      "type": "trustpilot_reviews",
      "brand": "Uplift",
      "url": "https://www.trustpilot.com/review/upliftdesk.com",
      "review_count": 50,
      "overall_rating": 4.5
    },
    {
      "type": "trustpilot_reviews",
      "brand": "Jarvis",
      "url": "https://www.trustpilot.com/review/fully.com",
      "review_count": 50,
      "overall_rating": 4.3
    }
  ],
  "_metadata": {
    "total_reviews_analyzed": 100,
    "total_reddit_posts": 0,
    "brands_analyzed": ["Uplift", "Jarvis"]
  }
}
```

## ✅ 前端修改

### 文件: `frontend/app/report/[taskId]/page.tsx`

在 `ReviewInsights` 组件中添加了：

1. **数据来源链接**（标题右侧）
   - 显示所有 Trustpilot 评论来源
   - 可点击跳转到原始评论页面
   - 悬停显示详细信息（评论数、平均评分）

2. **元数据统计**（标题下方）
   - 分析评论数
   - 分析品牌列表
   - Reddit 讨论数（如果有）

### UI 效果

```
⭐ 评论洞察                                    数据来源: [🔗 Uplift Trustpilot] [🔗 Jarvis Trustpilot]

分析评论数: 100 | 品牌: Uplift, Jarvis

📊 情感分布
[正面评论] [中性评论] [负面评论]

🏷️ 主题标签
[稳定性] [价格] [客服] ...

✅ Top 5 正面洞察
...

⚠️ Top 5 负面洞察
...
```

## 🎨 样式说明

### 数据来源链接
- 蓝色背景 (`bg-blue-50`)
- 圆角标签样式 (`rounded-full`)
- 悬停效果 (`hover:bg-blue-100`)
- 外部链接图标
- Tooltip 显示详细信息

### 元数据统计
- 灰色背景 (`bg-gray-50`)
- 小字体 (`text-sm`)
- 水平排列，间距适中

## 📊 数据流

```
1. Orchestrator._fetch_review_data()
   ↓ 添加 _source 字段到每个品牌的评论数据
   
2. Orchestrator._analyze_reviews()
   ↓ 从 review_data 提取 _source 信息
   ↓ 添加 _sources 和 _metadata 到分析结果
   
3. API 返回 review_insights
   ↓ 包含 _sources 和 _metadata
   
4. 前端 ReviewInsights 组件
   ↓ 显示数据来源链接
   ↓ 显示元数据统计
```

## ✅ 测试验证

运行调研后，检查：

1. **后端日志**：确认 `_sources` 和 `_metadata` 被添加
2. **API 响应**：检查 `review_insights` 包含溯源信息
3. **前端显示**：
   - 标题右侧显示数据来源链接
   - 链接可点击，跳转到 Trustpilot
   - 悬停显示详细信息
   - 元数据统计正确显示

## 🔍 示例

### Trustpilot 链接格式
- Uplift: `https://www.trustpilot.com/review/upliftdesk.com`
- Jarvis: `https://www.trustpilot.com/review/fully.com`
- Vari: `https://www.trustpilot.com/review/vari.com`

### Tooltip 内容
```
Uplift - 50 条评论，平均 4.5 星
```

## 📝 注意事项

1. **向后兼容**：如果 `_sources` 不存在，不显示数据来源部分
2. **错误处理**：如果 URL 无效，链接仍然显示但可能无法访问
3. **性能**：溯源信息不影响 LLM 分析性能（只是元数据）
4. **隐私**：不暴露用户个人信息，只显示公开的评论来源

## 🚀 后续优化

1. **添加更多来源**：
   - Amazon 评论
   - Reddit 讨论
   - YouTube 评论

2. **改进 UI**：
   - 添加来源图标（Trustpilot logo）
   - 显示评论时间范围
   - 添加数据新鲜度指示器

3. **增强功能**：
   - 按来源筛选洞察
   - 显示每个来源的情感分布
   - 导出溯源报告

