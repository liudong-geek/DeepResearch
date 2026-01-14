# 价格置信度问题解决方案

> **日期**: 2026-01-14  
> **优先级**: P0  
> **状态**: ✅ 已实施（阶段 1）

---

## 🎯 问题回顾

**用户反馈**：价格对比中显示的价格与溯源链接点进去看到的价格不一致。

**根本原因**：
- 使用启发式算法从 HTML 中提取价格
- 页面包含多个价格（原价、折扣价、配件价格等）
- 算法无法准确识别"主产品当前价格"

---

## ✅ 已实施的解决方案（阶段 1）

### 1. 后端：添加价格置信度元数据

**文件**: `backend/mcp_servers/ecommerce/scrapers/generic.py`

**修改**：
- `_extract_price_from_html()` 方法现在返回 `(price, metadata)`
- metadata 包含：
  - `confidence`: 置信度等级（high/medium/low/none）
  - `method`: 提取方法
  - `warning`: 警告信息
  - `all_prices_found`: 找到的价格数量
  - `candidates`: 候选价格数量

**置信度等级**：

| 等级 | 条件 | 说明 |
|------|------|------|
| `none` | 未找到价格 | 需人工验证 |
| `low` | 使用降级方案 | 价格可能不准确，强烈建议验证 |
| `medium` | 使用启发式算法 | 建议验证 |
| `high` | 使用结构化数据（未实现） | 可信度高 |

**示例输出**：
```python
price, metadata = _extract_price_from_html(html)
# price = 599.99
# metadata = {
#     "confidence": "medium",
#     "method": "heuristic_main_product",
#     "warning": "使用启发式算法提取，建议验证",
#     "all_prices_found": 15,
#     "candidates": 3
# }
```

---

### 2. 后端：在产品数据中添加置信度字段

**新增字段**：
- `price_confidence`: 置信度等级
- `price_extraction_method`: 提取方法
- `price_warning`: 警告信息（合并了置信度警告和异常价格警告）

**示例**：
```json
{
  "brand": "Uplift",
  "price": 599.99,
  "price_confidence": "medium",
  "price_extraction_method": "heuristic_main_product",
  "price_warning": "使用启发式算法提取，建议验证"
}
```

---

### 3. 前端：显示价格置信度警告

**文件**: `frontend/app/report/[taskId]/page.tsx`

**修改**：
- 检测价格警告（从 positioning 中提取）
- 有警告时显示黄色边框和背景
- 显示 ⚠️ 警告图标
- 添加"点击验证价格"链接

**UI 效果**：

#### 正常价格（无警告）
```
┌─────────────────────────────┐
│ Uplift [1]                  │
│ $599.99                     │
│ 中端定位，性价比高          │
└─────────────────────────────┘
```

#### 需验证价格（有警告）
```
┌─────────────────────────────┐ ← 黄色边框+背景
│ Uplift [1]                  │
│ $599.99 ⚠️                  │ ← 警告图标
│ 使用启发式算法，建议验证    │
│ 点击验证价格 →              │ ← 验证链接
└─────────────────────────────┘
```

---

## 🎨 UI 设计

### 颜色方案

- **正常价格**: 灰色边框 (border-gray-200)
- **需验证价格**: 黄色边框 + 黄色背景 (border-yellow-300 bg-yellow-50)
- **警告图标**: 黄色 ⚠️ (text-yellow-600)
- **验证链接**: 蓝色下划线 (text-blue-600 underline)

### 交互设计

1. **警告图标**: 鼠标悬停显示 "价格需要人工验证"
2. **验证链接**: 点击打开原始产品页面（新标签页）
3. **视觉区分**: 黄色背景让需验证的价格一目了然

---

## 📊 置信度判断逻辑

### 后端判断

```python
if main_product_prices:
    # 找到主产品价格范围内的价格
    return price, {
        "confidence": "medium",
        "method": "heuristic_main_product",
        "warning": "使用启发式算法提取，建议验证"
    }
elif secondary_prices:
    # 使用次优价格
    return price, {
        "confidence": "low",
        "method": "heuristic_secondary",
        "warning": "未找到主产品价格，使用次优价格，需人工验证"
    }
else:
    # 降级方案
    return price, {
        "confidence": "low",
        "method": "fallback_min_reasonable",
        "warning": "使用降级方案，价格可能不准确，强烈建议人工验证"
    }
```

### 前端判断

```typescript
const hasWarning = info.positioning && (
  info.positioning.includes('价格异常') || 
  info.positioning.includes('需人工核实') ||
  info.positioning.includes('需验证')
)
```

---

## ✅ 验证清单

- [x] 后端：`_extract_price_from_html()` 返回元数据
- [x] 后端：添加 `price_confidence` 字段
- [x] 后端：添加 `price_extraction_method` 字段
- [x] 后端：合并价格警告信息
- [x] 前端：检测价格警告
- [x] 前端：显示黄色边框和背景
- [x] 前端：显示警告图标
- [x] 前端：添加验证链接

---

## 🚀 下一步计划

### 阶段 2: 改进价格抽取算法（本周）

- [ ] 添加结构化数据提取（JSON-LD, microdata）
- [ ] 添加品牌特定的 CSS 选择器
- [ ] 改进价格范围判断逻辑
- [ ] 提高 `high` 置信度价格的比例

### 阶段 3: 添加价格验证机制（下周）

- [ ] 对比多个来源的价格
- [ ] 检测价格异常（过高/过低）
- [ ] 添加价格历史追踪
- [ ] 提供价格趋势分析

---

## 📝 相关文件

1. **问题分析**: `PRICE_CONFIDENCE_ISSUE.md`
2. **后端修改**: `backend/mcp_servers/ecommerce/scrapers/generic.py`
3. **前端修改**: `frontend/app/report/[taskId]/page.tsx`

---

## 💡 用户指南

### 如何使用价格验证功能

1. **查看价格对比**：在竞品对比表中查看各品牌价格
2. **识别警告**：黄色背景的价格卡片表示需要验证
3. **查看警告信息**：阅读价格下方的警告说明
4. **验证价格**：点击"点击验证价格 →"链接，打开原始页面
5. **对比确认**：对比报告中的价格和原始页面的价格
6. **反馈问题**：如发现价格不一致，请反馈给开发团队

---

## ✅ 总结

**问题**：价格数据不准确，用户无法信任

**解决方案**：
- ✅ 添加价格置信度元数据（后端）
- ✅ 显示价格警告和验证链接（前端）
- ✅ 提高数据透明度，让用户知道哪些价格需要验证

**效果**：
- 用户可以清楚地看到哪些价格需要验证
- 提供一键验证功能，方便用户核实
- 提高了工具的可信度和透明度

**下一步**：
- 改进价格抽取算法，提高准确性
- 添加价格验证机制，自动检测异常

---

**实施人**: AI Assistant  
**实施时间**: 2026-01-14  
**状态**: ✅ 阶段 1 完成

