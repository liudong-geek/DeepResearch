# 使用阿里云通义千问 Qwen 配置指南

## 为什么选择 Qwen？

✅ **国内可用** - 无需国际网络，访问速度快  
✅ **价格便宜** - 比 OpenAI 便宜 5-10 倍  
✅ **性能优秀** - Qwen-Plus 性能接近 GPT-4  
✅ **中文友好** - 对中文理解更好  
✅ **兼容 OpenAI API** - 无需修改代码  

## 快速开始（5 分钟）

### 1. 获取 API Key

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 登录/注册阿里云账号
3. 开通 **DashScope 服务**（免费开通）
4. 点击 **API-KEY 管理** → **创建新的 API-KEY**
5. 复制生成的 API Key（格式：`sk-xxx`）

### 2. 配置环境变量

编辑项目根目录的 `.env` 文件：

```bash
# 使用 Qwen
LLM_PROVIDER=qwen
LLM_API_KEY=sk-your-qwen-api-key-here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

### 3. 测试配置

```bash
cd backend
export LLM_PROVIDER=qwen
export LLM_API_KEY=sk-your-qwen-api-key-here
.venv/bin/python ../test_end_to_end.py
```

**预期输出**：
```
✅ OPENAI_API_KEY 已设置
使用 Qwen 模型: qwen-plus
✅ 测试完成！
```

## 模型选择

| 模型 | 性能 | 速度 | 价格 | 推荐场景 |
|------|------|------|------|---------|
| **qwen-turbo** | ⭐⭐⭐ | ⚡⚡⚡ | 💰 | 日常任务、快速响应 |
| **qwen-plus** | ⭐⭐⭐⭐ | ⚡⚡ | 💰💰 | **推荐**，平衡性能和成本 |
| **qwen-max** | ⭐⭐⭐⭐⭐ | ⚡ | 💰💰💰 | 复杂任务、高质量输出 |
| **qwen-long** | ⭐⭐⭐⭐ | ⚡ | 💰💰 | 超长文本（1M tokens） |

### 价格对比（截至 2024 年）

| 模型 | 输入价格 | 输出价格 | vs GPT-4o-mini |
|------|---------|---------|----------------|
| qwen-turbo | ¥0.3/百万 tokens | ¥0.6/百万 tokens | **便宜 10x** |
| qwen-plus | ¥0.8/百万 tokens | ¥2/百万 tokens | **便宜 5x** |
| qwen-max | ¥20/百万 tokens | ¥60/百万 tokens | 相当 |

## 配置示例

### 示例 1: 使用 Qwen-Plus（推荐）

```bash
# .env
LLM_PROVIDER=qwen
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

### 示例 2: 使用 Qwen-Turbo（最便宜）

```bash
# .env
LLM_PROVIDER=qwen
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

### 示例 3: 使用 Qwen-Max（最强性能）

```bash
# .env
LLM_PROVIDER=qwen
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-max
```

## 常见问题

### Q1: 如何获取免费额度？

新用户注册后会获得：
- **免费额度**：100 万 tokens（约 ¥1-2）
- **有效期**：3 个月

### Q2: API Key 格式是什么？

Qwen API Key 格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxx`

### Q3: 如何充值？

1. 访问 [DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 点击 **账户管理** → **充值**
3. 最低充值 ¥10

### Q4: 支持哪些功能？

✅ Chat Completions（对话）  
✅ JSON Mode（结构化输出）  
✅ Function Calling（函数调用）  
✅ Streaming（流式输出）  
❌ Vision（图像理解，需使用 qwen-vl 系列）  

### Q5: 如何切换回 OpenAI？

修改 `.env` 文件：

```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-4o-mini
```

### Q6: 报错 "insufficient_quota"？

**原因**：API Key 余额不足

**解决方案**：
1. 检查余额：[DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 充值或使用新的 API Key

### Q7: 报错 "invalid_api_key"？

**原因**：API Key 无效或格式错误

**解决方案**：
1. 检查 API Key 是否正确复制
2. 确认 API Key 已启用
3. 重新生成 API Key

## 性能对比

基于 DeepResearch 实际测试：

| 指标 | Qwen-Plus | GPT-4o-mini |
|------|-----------|-------------|
| 响应速度 | ~2 秒 | ~2 秒 |
| 中文质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 英文质量 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 成本 | ¥0.02/次 | ¥0.10/次 |
| 国内访问 | ✅ 快速 | ❌ 需要代理 |

## 推荐配置

### 开发环境

```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo  # 快速、便宜
```

### 生产环境

```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-plus  # 平衡性能和成本
```

### 高质量场景

```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max  # 最强性能
```

## 更多资源

- [Qwen 官方文档](https://help.aliyun.com/zh/dashscope/)
- [API 参考](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)
- [价格说明](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-metering-and-billing)
- [模型对比](https://help.aliyun.com/zh/dashscope/developer-reference/model-square)

