# 数据统计显示优化

> **更新时间**: 2026-01-14  
> **优先级**: P1  
> **状态**: ✅ 已完成

---

## 🎯 优化目标

优化数据概览中的"讨论/评论"统计卡片，使其更智能地显示数据：

- **有 Reddit 数据时**：显示 "Reddit 讨论" 数量
- **无 Reddit 数据时**：显示 "评论数据" 数量（来自 Trustpilot）

---

## 📊 修改前后对比

### 修改前

```typescript
<div className="bg-orange-50 rounded-lg p-4 text-center">
  <div className="text-2xl font-bold text-orange-600">
    {result.reddit_discussions?.length || 0}
  </div>
  <div className="text-sm text-gray-600">Reddit 讨论</div>
</div>
```

**问题**：
- ❌ 标签固定为 "Reddit 讨论"
- ❌ 没有 Reddit 数据时显示 `0`，不够直观
- ❌ 无法展示实际获取的评论数据数量

### 修改后

```typescript
<div className="bg-orange-50 rounded-lg p-4 text-center">
  <div className="text-2xl font-bold text-orange-600">
    {(() => {
      // 优先显示 Reddit 讨论数量
      const redditCount = result.reddit_discussions?.length || 
        (typeof result.metadata?.data_sources === 'object' 
          ? result.metadata.data_sources.reddit_posts 
          : 0) || 0;
      
      // 如果没有 Reddit 数据，显示评论数据数量
      if (redditCount === 0) {
        return (typeof result.metadata?.data_sources === 'object'
          ? result.metadata.data_sources.reviews
          : 0) || 0;
      }
      
      return redditCount;
    })()}
  </div>
  <div className="text-sm text-gray-600">
    {(() => {
      const redditCount = result.reddit_discussions?.length || 
        (typeof result.metadata?.data_sources === 'object' 
          ? result.metadata.data_sources.reddit_posts 
          : 0) || 0;
      return redditCount > 0 ? 'Reddit 讨论' : '评论数据';
    })()}
  </div>
</div>
```

**优势**：
- ✅ 动态标签：根据数据类型显示 "Reddit 讨论" 或 "评论数据"
- ✅ 智能降级：优先显示 Reddit，无数据时显示评论
- ✅ 更直观：用户能看到实际获取的数据数量

---

## 🔍 逻辑说明

### 数据优先级

1. **第一优先级**：`result.reddit_discussions?.length`
   - 直接从返回数据中获取 Reddit 讨论数组长度

2. **第二优先级**：`result.metadata.data_sources.reddit_posts`
   - 从元数据中获取 Reddit 讨论数量

3. **降级方案**：`result.metadata.data_sources.reviews`
   - 如果 Reddit 数据为 0，显示评论数据数量

### 标签逻辑

```typescript
redditCount > 0 ? 'Reddit 讨论' : '评论数据'
```

- **有 Reddit 数据**：显示 "Reddit 讨论"
- **无 Reddit 数据**：显示 "评论数据"

---

## 📋 使用场景

### 场景 1：成功获取 Reddit 数据

```json
{
  "reddit_discussions": [{...}, {...}, {...}],
  "metadata": {
    "data_sources": {
      "reddit_posts": 3,
      "reviews": 50
    }
  }
}
```

**显示结果**：
- 数字：`3`
- 标签：`Reddit 讨论`

---

### 场景 2：Reddit 获取失败，有评论数据

```json
{
  "reddit_discussions": [],
  "metadata": {
    "data_sources": {
      "reddit_posts": 0,
      "reviews": 50
    }
  }
}
```

**显示结果**：
- 数字：`50`
- 标签：`评论数据`

---

### 场景 3：两者都没有数据

```json
{
  "reddit_discussions": [],
  "metadata": {
    "data_sources": {
      "reddit_posts": 0,
      "reviews": 0
    }
  }
}
```

**显示结果**：
- 数字：`0`
- 标签：`评论数据`

---

## 🎨 UI 效果

### 有 Reddit 数据时

```
┌─────────────────────┐
│        3            │  ← 橙色大字
│   Reddit 讨论       │  ← 灰色小字
└─────────────────────┘
```

### 无 Reddit 数据时

```
┌─────────────────────┐
│        50           │  ← 橙色大字
│    评论数据         │  ← 灰色小字
└─────────────────────┘
```

---

## ✅ 验证清单

- [x] 修改代码完成
- [x] 逻辑测试通过
- [x] 前端服务器重启
- [x] 数据优先级正确
- [x] 标签动态切换正确
- [x] 降级逻辑正确

---

## 📝 相关文件

- **修改文件**: `frontend/app/report/[taskId]/page.tsx`
- **修改位置**: 第 211-239 行
- **组件**: 数据概览统计卡片

---

## 🚀 后续优化建议

### P2 优先级

1. **添加图标区分**
   ```typescript
   {redditCount > 0 ? '💬 Reddit 讨论' : '⭐ 评论数据'}
   ```

2. **添加 Tooltip 说明**
   - 鼠标悬停时显示数据来源详情
   - 例如："来自 Trustpilot 的 50 条评论"

3. **颜色区分**
   - Reddit 数据：橙色（当前）
   - 评论数据：蓝色或绿色

---

## ✅ 总结

**优化完成！** 数据统计卡片现在能够：

- ✅ 智能显示：优先 Reddit，降级评论
- ✅ 动态标签：根据数据类型自动切换
- ✅ 用户友好：始终显示有意义的数据

**用户体验提升**：用户现在能清楚地看到实际获取的数据数量和类型，而不是看到一个无意义的 `0`。

---

**更新人**: AI Assistant  
**更新时间**: 2026-01-14  
**状态**: ✅ 已完成并验证

