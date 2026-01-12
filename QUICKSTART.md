# DeepResearch 快速启动指南

## 🚀 5 分钟快速体验

### 前置要求

- Python 3.11+
- Node.js 18+
- OpenAI API Key（可选，用于 LLM 功能）

### 1. 安装依赖

```bash
# 后端依赖
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cd ..

# 前端依赖
cd frontend
npm install
cd ..
```

### 2. 配置 LLM（必需）

#### 方式 1: 使用 Qwen（推荐，国内可用）

```bash
# 编辑 .env 文件
LLM_PROVIDER=qwen
LLM_API_KEY=your-qwen-api-key-here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus

# 或者使用环境变量
export LLM_PROVIDER=qwen
export LLM_API_KEY='your-qwen-api-key'
```

**获取 Qwen API Key**：
1. 访问 https://dashscope.console.aliyun.com/
2. 登录/注册阿里云账号
3. 创建 API Key
4. 详细教程：[docs/QWEN_SETUP.md](docs/QWEN_SETUP.md)

#### 方式 2: 使用 OpenAI（需要国际网络）

```bash
# 编辑 .env 文件
LLM_PROVIDER=openai
LLM_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o-mini

# 或者使用环境变量
export OPENAI_API_KEY='your-api-key-here'
```

### 3. 运行测试

#### 测试 LLM 配置（推荐先运行）

```bash
# 测试 Qwen 配置
export LLM_PROVIDER=qwen
export LLM_API_KEY='your-qwen-api-key'
cd backend
.venv/bin/python ../test_qwen.py
```

**预期输出**：
```
✅ 所有测试通过！
🎉 Qwen 配置成功！可以开始使用了。
```

#### 测试数据抓取（不需要 API Key）

```bash
cd backend
unset LLM_API_KEY  # 清除 API Key，只测试数据抓取
.venv/bin/python ../test_end_to_end.py
```

**预期输出**：
```
✅ 数据抓取测试完成！成功: 2/2
💾 产品数据已保存到: test_product_data.json
```

#### 测试完整流程（需要 API Key）

```bash
# 使用 Qwen
export LLM_PROVIDER=qwen
export LLM_API_KEY='your-qwen-api-key'
cd backend
.venv/bin/python ../test_end_to_end.py

# 或使用 OpenAI
export LLM_PROVIDER=openai
export LLM_API_KEY='your-openai-api-key'
cd backend
.venv/bin/python ../test_end_to_end.py
```

**预期输出**：
```
✅ 测试完成！
📊 报告摘要:
   耗时: 24.5 秒
⚡ 效率对比:
   人工: 8 小时
   工具: 24.5 秒
   提速: 1177x
```

### 4. 启动开发环境

```bash
# 方式 1: 使用启动脚本（推荐）
./start_dev.sh

# 方式 2: 手动启动
# 终端 1 - 后端
cd backend
.venv/bin/uvicorn api.main:app --reload --port 8000

# 终端 2 - 前端
cd frontend
npm run dev
```

### 5. 访问应用

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 📖 使用流程

### 1. 选择竞品

在首页选择要分析的竞品：
- Uplift ✅
- Vari ✅
- Jarvis ⚠️（可能被重定向）

### 2. 启动调研

点击"开始调研"按钮，系统会：
1. 抓取竞品产品信息
2. 使用 LLM 生成竞品对比表
3. 使用 LLM 生成行动计划

### 3. 查看报告

调研完成后，自动跳转到报告页面，展示：
- ⚡ 效率对比
- 📊 竞品对比表
- 🎯 行动计划

## 🧪 测试文件说明

| 文件 | 说明 | 需要 API Key |
|------|------|--------------|
| `test_ecommerce.py` | 测试 E-commerce 爬虫 | ❌ |
| `test_orchestrator_no_llm.py` | 测试数据抓取（无 LLM） | ❌ |
| `test_end_to_end.py` | 完整端到端测试 | ✅ |
| `test_api.py` | 测试 FastAPI 接口 | ❌ |

## 🐛 常见问题

### Q1: Playwright 浏览器启动失败

```bash
# 重新安装浏览器
cd backend
.venv/bin/playwright install chromium
```

### Q2: OpenAI API 配额不足

**错误**: `Error code: 429 - insufficient_quota`

**解决方案**:
- 检查 API Key 是否有效
- 检查账户余额
- 或者先运行不需要 LLM 的测试

### Q3: 前端无法连接后端

**检查**:
- 后端是否在 8000 端口运行
- CORS 是否正确配置
- 环境变量 `NEXT_PUBLIC_API_URL` 是否正确

### Q4: Jarvis 爬虫被重定向

**原因**: Jarvis 网站有反爬虫机制

**解决方案**:
- 暂时只选择 Uplift 和 Vari
- 或者添加更真实的浏览器指纹

## 📊 性能指标

基于实际测试：

| 指标 | 数值 |
|------|------|
| 数据抓取成功率 | 2/3 (67%) |
| 平均抓取时间 | ~10 秒/竞品 |
| LLM 生成时间 | ~2 秒/任务 |
| 总耗时 | ~25 秒 |
| 相比人工提速 | **1177x** |

