# SEO MCP Server 配置指南

## 概述

SEO MCP Server 提供 Google 搜索和 SEO 分析功能，使用 **Google Custom Search JSON API**。

**免费配额**: 100 次/天

---

## 配置步骤

### 1. 获取 Google Custom Search API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建或选择一个项目
3. 启用 **Custom Search API**:
   - 在左侧菜单中选择 "APIs & Services" > "Library"
   - 搜索 "Custom Search API"
   - 点击 "Enable"
4. 创建 API 凭据:
   - 在左侧菜单中选择 "APIs & Services" > "Credentials"
   - 点击 "Create Credentials" > "API Key"
   - 复制生成的 API Key

**参考文档**: https://developers.google.com/custom-search/v1/overview

---

### 2. 创建 Custom Search Engine

1. 访问 [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. 点击 "Add" 创建新的搜索引擎
3. 配置搜索引擎:
   - **Sites to search**: 输入 `www.google.com` (搜索整个网络)
   - **Name**: 输入一个名称，如 "DeepResearch SEO"
   - 点击 "Create"
4. 在搜索引擎设置中:
   - 找到 "Search engine ID" (cx 参数)
   - 复制这个 ID
5. **重要**: 启用 "Search the entire web":
   - 在 "Basics" 标签页中
   - 打开 "Search the entire web" 开关

---

### 3. 配置环境变量

在项目根目录的 `.env` 文件中添加:

```bash
# Google Search API 配置
GOOGLE_SEARCH_API_KEY=your-api-key-here
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id-here
```

---

## 功能说明

### 1. Google 搜索 (`google_search`)

执行 Google 搜索，返回搜索结果。

**参数**:
- `query` (必填): 搜索关键词
- `market` (可选): 市场代码，如 `us`, `uk`，默认 `us`
- `num_results` (可选): 返回结果数量，最多 10，默认 10

**示例**:
```python
result = await seo_server.call_tool(
    "google_search",
    {
        "query": "standing desk",
        "market": "us",
        "num_results": 10
    }
)
```

---

### 2. 竞品排名分析 (`analyze_competitor_rankings`)

分析竞品在搜索结果中的排名。

**参数**:
- `keyword` (必填): 搜索关键词
- `competitors` (必填): 竞品品牌列表
- `market` (可选): 市场代码，默认 `us`

**示例**:
```python
result = await seo_server.call_tool(
    "analyze_competitor_rankings",
    {
        "keyword": "standing desk",
        "competitors": ["Uplift", "Jarvis", "Vari", "FlexiSpot"],
        "market": "us"
    }
)
```

---

### 3. SERP 特性 (`get_serp_features`)

获取搜索结果页特征（Top 结果）。

**参数**:
- `query` (必填): 搜索关键词
- `market` (可选): 市场代码，默认 `us`

**示例**:
```python
result = await seo_server.call_tool(
    "get_serp_features",
    {
        "query": "best standing desk",
        "market": "us"
    }
)
```

---

## 测试

运行测试脚本验证配置:

```bash
python test_seo_mcp.py
```

---

## 配额管理

- **免费配额**: 100 次/天
- **计费**: 超过免费配额后，$5/1000 次请求
- **限速**: SEO MCP Server 默认限速 1 次/秒，保护配额

**查看配额使用情况**:
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 选择项目
3. 进入 "APIs & Services" > "Dashboard"
4. 查看 "Custom Search API" 的使用情况

---

## 注意事项

1. **API 限制**:
   - 每次搜索最多返回 10 个结果
   - 不支持 Featured Snippet、People Also Ask 等高级 SERP 特性
   - 这些是 Google Custom Search API 的固有限制

2. **缓存策略**:
   - SEO 数据默认缓存 7 天
   - 减少 API 调用，节省配额

3. **未配置时的行为**:
   - 如果未配置 API，SEO 功能将返回空结果
   - 不会影响其他 MCP Server 的正常运行

---

## 故障排查

### 问题 1: "API key not valid"

**原因**: API Key 无效或未启用 Custom Search API

**解决方案**:
1. 检查 API Key 是否正确
2. 确认已启用 Custom Search API
3. 检查 API Key 的限制设置（IP、Referrer 等）

---

### 问题 2: "Invalid Value" 或 "cx parameter is invalid"

**原因**: Search Engine ID 无效

**解决方案**:
1. 检查 Search Engine ID 是否正确
2. 确认搜索引擎已启用 "Search the entire web"

---

### 问题 3: 配额已用完

**原因**: 超过 100 次/天的免费配额

**解决方案**:
1. 等待第二天配额重置
2. 或启用计费（$5/1000 次）
3. 利用缓存减少 API 调用

---

## 参考资源

- [Google Custom Search JSON API 文档](https://developers.google.com/custom-search/v1/overview)
- [Programmable Search Engine 控制台](https://programmablesearchengine.google.com/)
- [Google Cloud Console](https://console.cloud.google.com/)

