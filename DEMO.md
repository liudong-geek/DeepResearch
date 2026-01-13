# DeepResearch 演示指南

> **版本**: 1.0.0  
> **更新时间**: 2026-01-13

---

## 🎯 演示目标

展示 DeepResearch 如何在几分钟内完成原本需要 8 小时的竞品调研工作。

---

## 📋 演示准备

### 1. 环境检查

```bash
# 检查 Python 版本
python --version  # 应该是 3.11+

# 检查 Node.js 版本
node --version  # 应该是 18+

# 检查依赖安装
cd backend && source .venv/bin/activate
python -c "import fastapi, httpx, bs4; print('✅ 后端依赖已安装')"

cd ../frontend
npm list next react  # 检查前端依赖
```

### 2. 配置 LLM API

```bash
# 编辑 backend/.env
LLM_PROVIDER=qwen  # 或 openai
LLM_API_KEY=your-api-key
LLM_MODEL=qwen-plus  # 或 gpt-4o-mini
```

### 3. 启动服务

```bash
# 方式 1: 使用启动脚本（推荐）
./start_dev.sh

# 方式 2: 手动启动
# 终端 1: 启动后端
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8001

# 终端 2: 启动前端
cd frontend
npm run dev
```

---

## 🎬 演示流程

### 第 1 步: 打开应用

1. 浏览器访问 `http://localhost:3000`
2. 看到 DeepResearch 主页

**演示要点**:
- 介绍项目背景（FlexiSpot 升降桌开品前调研）
- 说明传统调研需要 8 小时，工具只需几分钟

---

### 第 2 步: 选择竞品

**操作**:
1. 查看竞品列表（按价格档次分类）
   - Premium: Uplift, Jarvis, Vari, Humanscale
   - Mid-range: FlexiSpot, Autonomous
   - Budget: IKEA, Monoprice

2. 选择 3-5 个竞品（建议选择）:
   - ✅ Uplift（Premium）
   - ✅ Jarvis（Premium）
   - ✅ FlexiSpot（Mid-range）
   - ✅ IKEA（Budget）

**演示要点**:
- 说明为什么选择这些竞品（覆盖不同价格档次）
- 展示可以添加自定义竞品

---

### 第 3 步: 启动调研

**操作**:
1. 点击"开始调研"按钮
2. 跳转到进度页面

**演示要点**:
- 展示实时进度条
- 说明 6 步调研流程：
  1. 抓取产品信息
  2. 抓取评论数据
  3. 抓取 Reddit 讨论
  4. 生成竞品对比表
  5. 分析评论洞察
  6. 生成行动计划

---

### 第 4 步: 查看报告

**操作**:
1. 等待调研完成（约 1-2 分钟）
2. 自动跳转到报告页面

**演示要点**:

#### 4.1 数据统计卡片
- 竞品数量: 4
- 产品数据: 4
- Reddit 讨论: 10
- 置信度: 70%+

#### 4.2 效率对比
- 人工耗时: 8 小时
- 工具耗时: 60 秒
- 提速倍数: 480x

#### 4.3 竞品对比表
- 价格对比（按品牌）
- 功能对比（列表展示）
- **重点**: 点击价格或功能后的引用气泡 `[1]`，展示数据来源

#### 4.4 Reddit 讨论
- 显示 5 个热门讨论
- 标题、内容预览、评分、评论数
- 点击"查看原帖"跳转到 Reddit

#### 4.5 行动计划
- 定价策略
- 上新策略
- 产品页建议

#### 4.6 数据来源
- 按类型分组（产品页、Reddit 讨论）
- 显示引用编号、URL、提取时间
- 显示提取的数据点

---

### 第 5 步: 演示引用溯源

**操作**:
1. 滚动到竞品对比表
2. 点击价格后的引用气泡 `[1]`
3. 弹出详情窗口

**演示要点**:
- 显示数据来源类型（🛒 产品页）
- 显示品牌名称（Uplift）
- 显示来源 URL（可点击跳转）
- 显示提取的数据点（price, title, features）
- 显示提取时间

**关键信息**:
- 每个结论都可以追溯到原始数据源
- 确保透明度和可审计性
- 避免 AI 幻觉

---

## 🎨 演示技巧

### 1. 强调核心价值

**效率提升**:
- "传统调研需要 8 小时，我们只需 1 分钟"
- "提速 480 倍"

**数据可信**:
- "每个结论都可以追溯到原始数据源"
- "点击引用气泡，立即查看数据来源"

**AI 驱动**:
- "使用 LLM 自动生成洞察和建议"
- "支持 OpenAI 和 Qwen（国内可用）"

### 2. 展示技术亮点

**MCP 架构**:
- "3 个专业化的 MCP Server"
- "E-commerce MCP: 8 个品牌"
- "Review MCP: 2 个平台"
- "Content MCP: 2 个来源（Reddit + 文章）"

**引用溯源**:
- "前端可点击引用气泡查看详情"
- "后端每个数据点都有 _source 字段"
- "按类型分组显示（产品页、Reddit、文章）"

**智能限速**:
- "自动限速，避免被封禁"
- "7 天缓存，提高效率"

### 3. 处理常见问题

**Q: Reddit 返回 403 错误？**
A: 这是 Reddit 的反爬虫机制，可以通过配置 Reddit API 凭证解决。

**Q: Amazon 评论抓取失败？**
A: Amazon 需要登录才能查看评论，可以使用 Selenium + 登录凭证。

**Q: LLM 返回空响应？**
A: 检查 API Key 是否正确，或者切换到其他 LLM 提供商。

---

## 📊 演示数据

### 示例竞品

| 品牌 | 价格 | 档次 | URL |
|-----|------|------|-----|
| Uplift | $599 | Premium | https://www.upliftdesk.com/... |
| Jarvis | $559 | Premium | https://www.fully.com/... |
| FlexiSpot | $299 | Mid-range | https://www.flexispot.com/... |
| IKEA | $249 | Budget | https://www.ikea.com/... |

### 预期输出

**竞品对比表**:
- 价格范围: $249 - $599
- 功能对比: 高度记忆、USB 充电、防碰撞等
- 材质对比: 钢材、铝合金等

**Reddit 讨论**:
- r/StandingDesk: 10 个热门帖子
- 用户关注点: 稳定性、噪音、性价比

**行动计划**:
- 定价策略: 建议定价 $399（Mid-range）
- 上新策略: 强调稳定性和静音
- 产品页建议: 突出高度记忆功能

---

## ✨ 演示总结

**核心信息**:
1. ⚡ 效率提升 480 倍（8 小时 → 1 分钟）
2. 🔍 数据可追溯（引用溯源）
3. 🤖 AI 驱动（LLM 生成洞察）
4. 📊 结构化输出（竞品对比、评论洞察、行动计划）
5. 🌐 国内可用（支持 Qwen）

**下一步**:
- 集成更多数据源（YouTube、TikTok）
- 优化 LLM 提示词
- 添加数据可视化（图表）
- 部署到生产环境

---

**演示时间**: 5-10 分钟  
**准备时间**: 5 分钟  
**状态**: ✅ 可演示

