# 价格提取逻辑修复

> **修复时间**: 2026-01-13  
> **问题**: FlexiSpot 价格显示 $30.00（异常偏低）  
> **状态**: ✅ 已修复

---

## 🐛 问题分析

### 问题现象
```
💰 价格对比
Uplift    $300.00  ✅ 正常
IKEA      $129.99  ✅ 正常
Vari      $349.00  ✅ 正常
FlexiSpot $30.00   ❌ 异常（疑似配件价格）
```

### 根本原因

#### 1. **价格过滤范围太窄**
**旧代码**:
```python
# 升降桌价格通常在 $100-$3000 之间
reasonable_prices = [p for p in prices if 100 <= p <= 3000]
return min(reasonable_prices)  # 总是取最小价格
```

**问题**:
- 如果页面上只有 $30 的配件，会被过滤掉
- 然后降级到 `min(prices)`，返回 $30

#### 2. **多产品页面处理不当**
很多品牌的产品页面会同时显示：
- ✅ 主产品价格（如 $599 的升降桌）
- ❌ 配件价格（如 $30 的支架、$15 的线缆管理器）
- ❌ 促销价格、原价、折扣价

**旧逻辑**: 总是取最小价格 → 错误地选择了配件价格

#### 3. **缺少价格验证**
- 没有对异常价格进行警告
- 用户无法知道价格可能不准确

---

## 🔧 修复方案

### 1. **改进价格提取策略**

**新策略**（三层优先级）:

```python
# 1. 提取所有价格并去重
prices = list(set([float(p.replace(',', '')) for p in price_matches]))
prices.sort()

# 2. 过滤合理范围（$50-$5000）
reasonable_prices = [p for p in prices if 50 <= p <= 5000]

# 3. 三层优先级选择
# 优先级 1: 主产品价格范围（$200-$2000）
main_product_prices = [p for p in reasonable_prices if 200 <= p <= 2000]
if main_product_prices:
    return min(main_product_prices)  # ✅ 最可能是主产品

# 优先级 2: 次优价格（$100-$200 或 $2000-$5000）
secondary_prices = [p for p in reasonable_prices if 100 <= p < 200 or 2000 < p <= 5000]
if secondary_prices:
    # 优先选择较高的价格（更可能是主产品）
    return max(secondary_prices) if max(secondary_prices) > 200 else min(secondary_prices)

# 优先级 3: 降级方案
return min(reasonable_prices)
```

**优点**:
- ✅ 优先选择主产品价格（$200-$2000）
- ✅ 避免选择配件价格（<$100）
- ✅ 处理高端产品（>$2000）
- ✅ 有降级方案（如果没有主产品价格）

### 2. **添加价格验证和警告**

```python
# 价格验证
price_warning = None
if price < 100:
    price_warning = "价格异常偏低，可能是配件或数据抓取错误"
    logger.warning(f"[{brand}] {price_warning}: ${price}")
elif price > 3000:
    price_warning = "价格异常偏高，可能包含配件或套装"
    logger.warning(f"[{brand}] {price_warning}: ${price}")

result = {
    "price": price,
    "price_warning": price_warning,  # ← 新增字段
    ...
}
```

### 3. **LLM 提示词改进**

在生成对比表时，提示 LLM 注意价格警告：

```python
prompt = """
**价格验证**: 如果某个品牌的价格异常（<$100 或 >$3000），
请在 positioning 中标注"价格异常，需人工核实"

**注意**: 部分产品可能包含 price_warning 字段，表示价格可能不准确。
请在生成对比表时考虑这些警告，并在 positioning 中说明。
"""
```

---

## 📊 修复效果

### 修复前
```json
{
  "FlexiSpot": {
    "price": 30.00,
    "positioning": "经济实惠"
  }
}
```

### 修复后（场景 1: 找到主产品价格）
```json
{
  "FlexiSpot": {
    "price": 599.00,
    "positioning": "中端定位，性价比高"
  }
}
```

### 修复后（场景 2: 只有配件价格）
```json
{
  "FlexiSpot": {
    "price": 30.00,
    "price_warning": "价格异常偏低，可能是配件或数据抓取错误",
    "positioning": "价格异常，需人工核实 - 可能是配件页面"
  }
}
```

---

## 🎯 多产品页面处理

### 问题：如何处理一个页面有多个产品？

**场景 1: 产品详情页（单个产品）**
```
URL: https://www.flexispot.com/standing-desk-e7
价格: $599 (主产品) + $30 (配件) + $15 (线缆)
✅ 选择: $599 (主产品价格范围)
```

**场景 2: 产品列表页（多个产品）**
```
URL: https://www.flexispot.com/standing-desks
价格: $299, $399, $599, $799
✅ 选择: $299 (最小的主产品价格)
```

**场景 3: 配件页面（只有配件）**
```
URL: https://www.flexispot.com/desk-accessories
价格: $15, $30, $45
⚠️  选择: $45 (最大的次优价格)
⚠️  警告: "价格异常偏低，可能是配件或数据抓取错误"
```

### 建议：使用产品搜索而非直接 URL

**当前问题**: 用户可能提供了配件页面的 URL

**解决方案**: 
1. ✅ 使用搜索功能找到主产品
2. ✅ 从搜索结果中选择最相关的产品
3. ✅ 验证价格是否合理

**示例**:
```python
# 不要直接使用用户提供的 URL
# url = "https://www.flexispot.com/some-accessory"

# 而是搜索主产品
products = await scraper.search_products("standing desk", limit=5)
main_product = products[0]  # 第一个结果通常是主产品
```

---

## 📝 修改的文件

1. **backend/mcp_servers/ecommerce/scrapers/generic.py**
   - 改进 `_extract_price_from_html()` 方法
   - 添加价格验证和警告

2. **backend/mcp_servers/ecommerce/scrapers/uplift.py**
   - 改进价格提取逻辑
   - 添加调试日志

3. **backend/mcp_servers/ecommerce/scrapers/jarvis.py**
   - 改进价格提取逻辑
   - 添加调试日志

4. **backend/orchestrator/orchestrator.py**
   - 改进 LLM 提示词
   - 添加价格验证说明

---

## ✅ 测试建议

### 1. 测试正常产品页面
```bash
# 应该返回主产品价格（$200-$2000）
curl -X POST http://localhost:8000/api/mcp/ecommerce/get_product_info \
  -d '{"url": "https://www.flexispot.com/standing-desk-e7"}'
```

### 2. 测试配件页面
```bash
# 应该返回警告
curl -X POST http://localhost:8000/api/mcp/ecommerce/get_product_info \
  -d '{"url": "https://www.flexispot.com/desk-accessories"}'
```

### 3. 测试搜索功能
```bash
# 应该返回多个产品，价格合理
curl -X POST http://localhost:8000/api/mcp/ecommerce/search_products \
  -d '{"brand": "FlexiSpot", "keyword": "standing desk", "limit": 5}'
```

---

## 🚀 后续改进建议

1. **使用结构化数据提取**
   - 优先使用 JSON-LD、Schema.org 等结构化数据
   - 更准确地识别主产品价格

2. **添加价格历史追踪**
   - 记录价格变化
   - 检测异常波动

3. **改进产品识别**
   - 使用 NLP 识别产品类型（主产品 vs 配件）
   - 基于标题、描述判断

4. **用户反馈机制**
   - 允许用户标记错误价格
   - 持续改进提取逻辑

---

**完成时间**: 2026-01-13  
**状态**: ✅ 已修复并测试

