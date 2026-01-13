# DeepResearch 项目文件结构

> **更新时间**: 2026-01-13  
> **总文件数**: 70+  
> **总代码量**: ~4860 行

---

## 📁 项目结构

```
DeepResearch/
├── 📄 文档 (17 个)
│   ├── README.md                           # 项目说明
│   ├── QUICKSTART.md                       # 快速开始指南
│   ├── DEMO.md                             # 演示指南
│   ├── PROJECT_COMPLETE_SUMMARY.md         # 项目完成总结
│   ├── CITATION_IMPLEMENTATION.md          # 引用溯源实现报告
│   ├── CONTENT_MCP_IMPLEMENTATION.md       # Content MCP 实现报告
│   ├── CONTENT_MCP_USAGE.md                # Content MCP 使用指南
│   ├── PROGRESS_SUMMARY.md                 # 项目进度总结
│   ├── ARCHITECTURE_AUDIT.md               # 架构审计
│   ├── DESIGN.md                           # 设计文档
│   ├── TROUBLESHOOTING.md                  # 故障排除
│   └── docs/QWEN_SETUP.md                  # Qwen 配置指南
│
├── 🐍 后端 (Backend)
│   ├── api/                                # FastAPI 应用
│   │   ├── main.py                         # 主应用入口
│   │   └── routes/                         # API 路由
│   │       ├── health.py                   # 健康检查
│   │       └── research.py                 # 调研 API
│   │
│   ├── mcp_servers/                        # MCP Server 集群
│   │   ├── shared/                         # 共享组件
│   │   │   ├── base_server.py              # 基础 MCP Server
│   │   │   ├── rate_limiter.py             # 限速器
│   │   │   └── cache_manager.py            # 缓存管理器
│   │   │
│   │   ├── ecommerce/                      # E-commerce MCP
│   │   │   ├── server.py                   # MCP Server 实现
│   │   │   └── scrapers/                   # 爬虫
│   │   │       ├── base.py                 # 基础爬虫
│   │   │       ├── uplift.py               # Uplift 爬虫
│   │   │       ├── jarvis.py               # Jarvis 爬虫
│   │   │       ├── vari.py                 # Vari 爬虫
│   │   │       ├── monoprice.py            # Monoprice 爬虫
│   │   │       └── generic.py              # 通用爬虫
│   │   │
│   │   ├── review/                         # Review MCP
│   │   │   ├── server.py                   # MCP Server 实现
│   │   │   └── scrapers/                   # 爬虫
│   │   │       ├── base.py                 # 基础爬虫
│   │   │       ├── amazon.py               # Amazon 爬虫
│   │   │       └── reddit.py               # Reddit 爬虫
│   │   │
│   │   └── content/                        # Content MCP
│   │       ├── server.py                   # MCP Server 实现
│   │       └── scrapers/                   # 爬虫
│   │           ├── base.py                 # 基础爬虫
│   │           ├── reddit.py               # Reddit 爬虫
│   │           └── article.py              # 文章爬虫
│   │
│   ├── orchestrator/                       # 调研编排器
│   │   └── orchestrator.py                 # 6 步调研流程
│   │
│   ├── db/                                 # 数据库（未使用）
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── tests/                              # 测试
│   │   └── test_mcp_server.py
│   │
│   └── utils/                              # 工具函数
│
├── 🖥️ 前端 (Frontend)
│   ├── app/                                # Next.js 应用
│   │   ├── layout.tsx                      # 根布局
│   │   ├── page.tsx                        # 主页（表单输入）
│   │   ├── report/[taskId]/page.tsx        # 报告页面
│   │   └── test/page.tsx                   # 测试页面
│   │
│   ├── components/                         # React 组件
│   │   ├── CitationBubble.tsx              # 引用气泡组件
│   │   ├── CitedText.tsx                   # 带引用文本组件
│   │   ├── CitationList.tsx                # 引用列表组件
│   │   └── citations.ts                    # 引用工具函数
│   │
│   ├── lib/                                # 库
│   │   └── api.ts                          # API 客户端 + 类型定义
│   │
│   ├── CITATION_USAGE.md                   # 引用组件使用指南
│   └── tailwind.config.ts                  # Tailwind 配置
│
└── 🧪 测试脚本 (6 个)
    ├── test_qwen.py                        # Qwen API 测试
    ├── test_end_to_end.py                  # 端到端测试
    ├── test_all_scrapers.py                # 所有爬虫测试
    ├── test_monoprice_only.py              # Monoprice 测试
    ├── test_anti_scraping.py               # 反爬虫测试
    └── test_improvements.py                # 改进测试
```

---

## 📊 文件统计

### 后端 (Python)

| 模块 | 文件数 | 代码行数 | 说明 |
|-----|--------|---------|------|
| **Shared** | 3 | ~400 | 限速器、缓存、基础 Server |
| **E-commerce MCP** | 7 | ~1200 | 8 个品牌爬虫 |
| **Review MCP** | 4 | ~400 | Amazon + Reddit |
| **Content MCP** | 4 | ~640 | Reddit + Article |
| **Orchestrator** | 1 | ~620 | 6 步调研流程 |
| **FastAPI** | 3 | ~100 | API 路由 |
| **测试** | 6 | ~300 | 各种测试脚本 |
| **总计** | **28** | **~3660** | |

### 前端 (TypeScript/TSX)

| 模块 | 文件数 | 代码行数 | 说明 |
|-----|--------|---------|------|
| **Pages** | 4 | ~800 | 主页、报告页、测试页 |
| **Components** | 4 | ~650 | 引用组件 |
| **Lib** | 1 | ~50 | API 客户端 |
| **总计** | **9** | **~1500** | |

### 文档 (Markdown)

| 类型 | 文件数 | 说明 |
|-----|--------|------|
| **用户文档** | 5 | README, QUICKSTART, DEMO, TROUBLESHOOTING |
| **实现报告** | 4 | CITATION, CONTENT_MCP, PROGRESS, PROJECT_COMPLETE |
| **设计文档** | 3 | DESIGN, ARCHITECTURE_AUDIT, IMPROVEMENT_PLAN |
| **其他** | 5 | 各种总结和修复记录 |
| **总计** | **17** | |

---

## 🎯 核心文件说明

### 后端核心

1. **`backend/orchestrator/orchestrator.py`** (620 行)
   - 6 步调研流程
   - LLM 集成
   - 引用溯源支持

2. **`backend/mcp_servers/ecommerce/server.py`** (200+ 行)
   - E-commerce MCP Server
   - 8 个品牌支持
   - 统一数据格式

3. **`backend/mcp_servers/content/server.py`** (200+ 行)
   - Content MCP Server
   - Reddit + Article 支持
   - 智能文本清理

4. **`backend/mcp_servers/shared/base_server.py`** (150+ 行)
   - 基础 MCP Server
   - 限速、缓存、日志

### 前端核心

1. **`frontend/app/report/[taskId]/page.tsx`** (485 行)
   - 报告展示页面
   - 竞品对比表
   - Reddit 讨论
   - 引用列表

2. **`frontend/components/CitationBubble.tsx`** (165 行)
   - 引用气泡组件
   - 可点击查看详情
   - 弹窗展示

3. **`frontend/components/CitationList.tsx`** (150 行)
   - 引用列表组件
   - 按类型分组
   - 统计信息

4. **`frontend/lib/api.ts`** (50+ 行)
   - API 客户端
   - TypeScript 类型定义

---

## 📚 文档清单

### 用户文档

1. **README.md** - 项目说明、快速开始
2. **QUICKSTART.md** - 详细的快速开始指南
3. **DEMO.md** - 演示指南（5-10 分钟）
4. **TROUBLESHOOTING.md** - 故障排除

### 实现报告

1. **PROJECT_COMPLETE_SUMMARY.md** - 项目完成总结
2. **CITATION_IMPLEMENTATION.md** - 引用溯源实现报告
3. **CONTENT_MCP_IMPLEMENTATION.md** - Content MCP 实现报告
4. **PROGRESS_SUMMARY.md** - 项目进度总结

### 使用指南

1. **CONTENT_MCP_USAGE.md** - Content MCP 使用指南
2. **frontend/CITATION_USAGE.md** - 引用组件使用指南
3. **docs/QWEN_SETUP.md** - Qwen 配置指南

### 设计文档

1. **DESIGN.md** - 系统设计文档
2. **ARCHITECTURE_AUDIT.md** - 架构审计
3. **IMPROVEMENT_PLAN.md** - 改进计划

---

## 🔧 配置文件

| 文件 | 说明 |
|-----|------|
| `backend/requirements.txt` | Python 依赖 |
| `backend/.env` | 环境变量（LLM API Key） |
| `frontend/package.json` | Node.js 依赖 |
| `frontend/tailwind.config.ts` | Tailwind CSS 配置 |
| `frontend/next.config.js` | Next.js 配置 |
| `frontend/.env.local` | 前端环境变量 |

---

## 🚀 启动脚本

| 脚本 | 说明 |
|-----|------|
| `start_dev.sh` | 启动开发环境（后端 + 前端） |
| `backend/main.py` | FastAPI 应用入口 |
| `frontend/package.json` | npm run dev / build / start |

---

## ✨ 总结

**项目规模**:
- 总文件数: 70+
- 总代码量: ~4860 行
- Python 代码: ~3660 行
- TypeScript 代码: ~1500 行
- 文档: 17 个

**代码质量**:
- ✅ 模块化设计
- ✅ 类型安全（TypeScript + Python 类型提示）
- ✅ 完整的文档
- ✅ 测试脚本

**下一步**:
- 添加单元测试
- 优化性能
- 部署到生产环境

---

**更新时间**: 2026-01-13  
**状态**: ✅ 核心功能完成

