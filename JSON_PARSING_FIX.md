# JSON 解析问题修复

> **修复日期**: 2026-01-14  
> **问题**: LLM 返回 markdown 格式的 JSON 导致解析失败  
> **状态**: ✅ 已修复

---

## 🐛 问题描述

### 错误信息
```
ERROR | ❌ 解析 LLM 响应失败: Expecting value: line 1 column 1 (char 0)
ERROR | 响应内容: ```json
{
  "topics": [
    {
      "name": "客服",
      "count": 24,
      ...
    }
  ]
}
```
```

### 问题原因

**LLM 返回格式**：
- Qwen 等 LLM 返回的 JSON 包裹在 markdown 代码块中（```json ... ```）
- 代码直接使用 `json.loads()` 解析，导致失败

**影响范围**：
- ❌ 评论洞察解析失败
- ⚠️ 竞品对比表（已有部分处理，但不完善）
- ⚠️ 行动计划（已有部分处理，但不完善）

---

## ✅ 修复方案

### 1. 创建统一的 JSON 清理函数

**位置**: `backend/orchestrator/orchestrator.py`

```python
def _clean_json_response(self, content: str) -> str:
    """清理 LLM 返回的 JSON 响应（移除 markdown 格式）"""
    cleaned = content.strip()
    
    # 移除 markdown 代码块标记
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]  # 移除 ```json
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]  # 移除 ```
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]  # 移除结尾的 ```
    
    return cleaned.strip()
```

**功能**：
- ✅ 移除 ````json` 开头
- ✅ 移除 ```` 开头（兼容简单格式）
- ✅ 移除 ```` 结尾
- ✅ 清理前后空白字符

---

### 2. 更新三个解析点

#### A. 竞品对比表（`_generate_comparison_table`）

**修改前**：
```python
if "```json" in content:
    json_str = content.split("```json")[1].split("```")[0].strip()
elif "```" in content:
    json_str = content.split("```")[1].split("```")[0].strip()
else:
    json_str = content.strip()

comparison = json.loads(json_str)
```

**修改后**：
```python
cleaned_content = self._clean_json_response(content)
comparison = json.loads(cleaned_content)
```

---

#### B. 评论洞察（`_analyze_reviews`）

**修改前**：
```python
# 直接解析，没有处理 markdown
analysis = json.loads(content)
```

**修改后**：
```python
cleaned_content = self._clean_json_response(content)
analysis = json.loads(cleaned_content)
```

---

#### C. 行动计划（`_generate_action_plan`）

**修改前**：
```python
if "```json" in content:
    json_str = content.split("```json")[1].split("```")[0].strip()
elif "```" in content:
    json_str = content.split("```")[1].split("```")[0].strip()
else:
    json_str = content.strip()

action_plan = json.loads(json_str)
```

**修改后**：
```python
cleaned_content = self._clean_json_response(content)
action_plan = json.loads(cleaned_content)
```

---

## 🧪 测试验证

### 测试脚本
`test_json_parsing.py`

### 测试结果
```
✅ Markdown JSON 格式 - 解析成功
✅ 纯 JSON 格式 - 解析成功
✅ 简单 Markdown 格式 - 解析成功
```

### 测试用例
1. **Markdown JSON**: ` ```json\n{...}\n``` ` ✅
2. **纯 JSON**: `{...}` ✅
3. **简单 Markdown**: ` ```\n{...}\n``` ` ✅

---

## 📊 修复效果

### 修复前
- ❌ 评论洞察：解析失败，返回空数据
- ⚠️ 竞品对比表：部分成功（取决于 LLM 返回格式）
- ⚠️ 行动计划：部分成功（取决于 LLM 返回格式）

### 修复后
- ✅ 评论洞察：稳定解析
- ✅ 竞品对比表：稳定解析
- ✅ 行动计划：稳定解析
- ✅ 统一处理逻辑，代码更简洁

---

## 🎯 关键改进

### 1. 统一处理
- ✅ 一个函数处理所有 JSON 清理
- ✅ 避免重复代码
- ✅ 更易维护

### 2. 兼容性
- ✅ 支持 ````json` 格式
- ✅ 支持 ```` 格式
- ✅ 支持纯 JSON 格式

### 3. 错误处理
- ✅ 保留原有的错误日志
- ✅ 显示原始响应（前 500 字符）
- ✅ 返回友好的错误信息

---

## 📝 后续建议

### 短期
- ✅ 已修复：JSON 解析问题
- ⚪ 监控：观察生产环境是否还有解析失败

### 中期
- ⚪ 优化：考虑使用 LLM 的 `response_format` 参数（OpenAI 支持）
- ⚪ 测试：添加更多边缘情况测试

### 长期
- ⚪ 考虑：使用结构化输出（如 Pydantic）
- ⚪ 考虑：添加 JSON Schema 验证

---

## ✅ 验证清单

- [x] 创建 `_clean_json_response` 函数
- [x] 更新竞品对比表解析
- [x] 更新评论洞察解析
- [x] 更新行动计划解析
- [x] 编写测试脚本
- [x] 验证测试通过
- [x] 更新文档

---

**修复完成时间**: 2026-01-14  
**修复人**: AI Assistant  
**状态**: ✅ 完成并验证

