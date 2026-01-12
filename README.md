# DeepResearch - 竞品调研智能体

> 基于 MCP (Model Context Protocol) 的自动化竞品调研系统，为 FlexiSpot 升降桌开品前提供市场洞察、竞品对比、用户评价分析和行动建议。

## 🎯 项目特点

- ✅ **引用溯源**：每个结论可追溯到原始数据源（URL + 引用片段）
- ✅ **MCP 架构**：垂直领域 MCP Server 集群，标准化数据采集能力
- ✅ **智能编排**：轻量级 Agent + LLM Function Calling，自动生成结构化报告
- ✅ **多 LLM 支持**：支持 OpenAI、Qwen（通义千问）等多种 LLM
- ✅ **国内可用**：支持阿里云 Qwen，无需国际网络
- ✅ **爬虫稳定**：限速/重试/去重/缓存/增量抓取机制
- ✅ **前端体验**：Next.js + shadcn/ui，实时进度 + 可视化报告
- ✅ **一键运行**：Docker Compose 统一编排所有服务

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                  前端 (Next.js + TypeScript)                 │
│              输入表单 → 进度追踪 → 报告展示                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP API / WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│              后端 (FastAPI + Python 3.11)                    │
│         Orchestrator → LLM → Report Generator                │
└──────────────────────┬──────────────────────────────────────┘
                       │ MCP Protocol
┌──────────────────────▼──────────────────────────────────────┐
│                   MCP Server 集群                            │
│  E-commerce │ Review │ Content │ SEO │ Social               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│         数据层 (PostgreSQL + pgvector + Redis)               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- Qwen API Key（推荐）或 OpenAI API Key

### 3 分钟快速体验

#### 1️⃣ 安装依赖

```bash
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 前端
cd ../frontend
npm install
```

#### 2️⃣ 配置 LLM（选择一种）

**方式 1: 使用 Qwen（推荐，国内可用）** 🔥

```bash
# 编辑 .env 文件
LLM_PROVIDER=qwen
LLM_API_KEY=your-qwen-api-key  # 从 https://dashscope.console.aliyun.com/ 获取
LLM_MODEL=qwen-plus
```

**方式 2: 使用 OpenAI（需要国际网络）**

```bash
# 编辑 .env 文件
LLM_PROVIDER=openai
LLM_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o-mini
```

📖 **详细配置教程**：
- [完整快速开始指南](QUICKSTART.md)

#### 3️⃣ 测试配置

```bash
cd backend
.venv/bin/python ../test_qwen.py  # 测试 Qwen
# 或
.venv/bin/python ../test_end_to_end.py  # 完整测试
```

#### 4️⃣ 启动应用

```bash
./start_dev.sh
```

访问：
- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8001
- **API 文档**: http://localhost:8001/docs

## 📁 项目结构

```
deep-research/
├── backend/              # Python 后端
│   ├── mcp_servers/      # MCP Server 集群
│   │   ├── shared/       # 共享模块（限速/缓存/基类）
│   │   ├── ecommerce/    # 电商产品数据
│   │   ├── review/       # 用户评论分析
│   │   ├── content/      # 测评内容
│   │   ├── seo/          # SEO/广告数据
│   │   └── social/       # 社交媒体
│   ├── orchestrator/     # 智能体编排层
│   ├── api/              # FastAPI 接口
│   ├── db/               # 数据库模型
│   └── tests/            # 测试
├── frontend/             # Next.js 前端
│   ├── app/              # App Router
│   ├── components/       # React 组件
│   └── lib/              # 工具库
├── docs/                 # 文档
├── scripts/              # 运维脚本
├── docker-compose.yml    # Docker 编排
├── Makefile              # 快捷命令
└── .env.example          # 环境变量模板
```

## 🛠️ 开发指南

### 常用命令

```bash
make dev        # 启动开发环境
make dev-bg     # 后台启动
make logs       # 查看日志
make test       # 运行测试
make stop       # 停止服务
make clean      # 清理缓存
```

### 开发工作流

1. **后端开发**：修改 `backend/` 代码后，FastAPI 自动重载
2. **前端开发**：修改 `frontend/` 代码后，Next.js 自动热更新
3. **MCP Server 开发**：参考 `docs/MCP_SERVERS.md`
4. **运行测试**：`make test`

## 📊 功能特性

### 输入
- 产品关键词：standing desk（固定）
- 目标市场：US（固定）
- 竞品列表：Uplift / Jarvis / Vari / Autonomous（可选）

### 输出
1. **竞品对比表**：价格带、卖点、痛点、材质、稳定性
2. **评论洞察**：主题标签（10-20个）、正/负面要点、典型语句
3. **行动计划**：运营/投放/产品/客服建议
4. **效率证明**：人工 vs 工具耗时对比

### 引用溯源
- 每个结论右上角显示 `[引用]` 图标
- 点击展开：引用片段 + 来源链接 + 时间戳
- 点击链接跳转到原始网页

## 🔧 配置说明

### 环境变量

```bash
# LLM API Keys（必填）
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 数据库（自动配置）
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/deep_research
REDIS_URL=redis://redis:6379/0

# 爬虫配置（可选）
SCRAPER_API_KEY=...  # 反爬虫备用方案
SERP_API_KEY=...     # Google 搜索 API
```

## 📚 文档

- [技术设计文档](./DESIGN.md) - 完整的架构设计和实施计划（800+ 行）
- [快速开始指南](./QUICKSTART.md) - 详细的安装和配置教程
- [当前状态报告](./CURRENT_STATUS.md) - 项目实现状态和测试结果
- [最终总结](./FINAL_SUMMARY.md) - 功能完成度和使用指南
- [故障排除](./TROUBLESHOOTING.md) - 常见问题和解决方案

## 🧪 测试

```bash
# 端到端测试（推荐）
make local-test-e2e

# 测试所有爬虫
cd backend && .venv/bin/python ../test_all_scrapers.py

# 测试 LLM 集成
cd backend && .venv/bin/python ../test_qwen.py
```

## 📈 性能指标

- **调研耗时**：3个竞品 < 5分钟
- **缓存命中率**：> 60%
- **爬虫成功率**：> 95%
- **测试覆盖率**：> 80%

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

## 📄 许可证

MIT License

## 👥 作者

- 项目负责人：[Your Name]
- 技术支持：[Team]

---

**当前状态**：🚧 开发中（Phase 1 - 项目基础搭建）

