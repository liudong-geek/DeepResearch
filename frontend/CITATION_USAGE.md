# 引用溯源组件使用指南

> **版本**: 1.0.0  
> **更新时间**: 2026-01-13

---

## 📖 简介

引用溯源组件提供了一套完整的 UI 组件，用于在报告中显示数据来源引用，确保每个结论都可以追溯到原始数据源。

---

## 🎨 组件列表

### 1. CitationBubble - 引用气泡

显示一个可点击的引用编号，点击后展开详细信息。

```tsx
import { CitationBubble, CitationSource } from '@/components/citations'

const source: CitationSource = {
  type: 'product_page',
  url: 'https://www.upliftdesk.com/...',
  brand: 'Uplift',
  extracted_at: '2026-01-13T22:00:00Z',
  data_points: ['price', 'title', 'features']
}

<CitationBubble number={1} source={source} />
```

**效果**: 显示一个蓝色的 `[1]` 气泡，点击后弹出详细信息。

---

### 2. CitedText - 带引用的文本

在文本后面显示引用气泡。

```tsx
import { CitedText } from '@/components/citations'

<CitedText 
  text="Uplift 的价格为 $599"
  sources={[source]}
/>
```

**效果**: `Uplift 的价格为 $599 [1]`

---

### 3. CitedParagraph - 带引用的段落

在段落末尾显示引用气泡。

```tsx
import { CitedParagraph } from '@/components/citations'

<CitedParagraph 
  content="Uplift 是市场上最受欢迎的升降桌品牌之一。"
  source={source}
/>
```

---

### 4. CitedListItem - 带引用的列表项

在列表项末尾显示引用气泡。

```tsx
import { CitedListItem } from '@/components/citations'

<ul>
  <CitedListItem 
    content="价格范围: $500-$800"
    source={source}
  />
  <CitedListItem 
    content="支持高度记忆功能"
    source={source}
  />
</ul>
```

---

### 5. CitationList - 引用来源列表

在报告底部显示所有引用来源的详细信息。

```tsx
import { CitationList } from '@/components/citations'

<CitationList 
  sources={allSources}
  title="📚 数据来源"
/>
```

**功能**:
- 按类型分组显示（产品页、评论、Reddit、文章）
- 显示统计信息
- 显示引用编号
- 显示提取时间
- 显示数据点标签

---

### 6. CitationManager - 引用管理器

用于管理多个引用来源，自动分配编号。

```tsx
import { CitationManager } from '@/components/citations'

const manager = new CitationManager()

// 添加引用
const num1 = manager.addSource(source1)  // 返回 1
const num2 = manager.addSource(source2)  // 返回 2
const num3 = manager.addSource(source1)  // 返回 1（去重）

// 获取所有引用
const allSources = manager.getAllSources()

// 清空
manager.clear()
```

---

## 🎯 数据结构

### CitationSource

```typescript
interface CitationSource {
  /** 来源类型 */
  type: 'product_page' | 'review' | 'reddit_post' | 'article' | 'error'
  
  /** 来源 URL */
  url: string
  
  /** 品牌名称（产品页） */
  brand?: string
  
  /** 子版块名称（Reddit） */
  subreddit?: string
  
  /** 域名（文章） */
  domain?: string
  
  /** 提取时间 */
  extracted_at: string
  
  /** 提取的数据点 */
  data_points?: string[]
}
```

---

## 💡 使用示例

### 示例 1: 在竞品对比表中使用

```tsx
function ComparisonTable({ data }: { data: any }) {
  return (
    <div>
      <h2>价格对比</h2>
      {Object.entries(data.price_comparison).map(([brand, info]: [string, any]) => (
        <div key={brand}>
          <CitedText 
            text={`${brand}: $${info.price}`}
            sources={info._sources || []}
          />
        </div>
      ))}
    </div>
  )
}
```

### 示例 2: 在行动计划中使用

```tsx
function ActionPlan({ data }: { data: any }) {
  return (
    <div>
      <h2>定价策略</h2>
      <CitedParagraph 
        content={data.pricing_strategy}
        source={data._source}
      />
    </div>
  )
}
```

### 示例 3: 提取所有引用

```tsx
function extractCitations(result: ResearchResult): CitationSource[] {
  const citations: CitationSource[] = []

  // 从产品数据提取
  if (result.comparison_table?.sources) {
    result.comparison_table.sources.forEach((source: any) => {
      if (source._source) {
        citations.push(source._source)
      }
    })
  }

  // 从 Reddit 讨论提取
  if (result.reddit_discussions) {
    result.reddit_discussions.forEach((post: any) => {
      if (post._source) {
        citations.push(post._source)
      }
    })
  }

  return citations
}
```

---

## 🎨 样式定制

### 颜色方案

不同类型的引用使用不同的颜色：

| 类型 | 颜色 | 图标 |
|-----|------|------|
| product_page | 蓝色 | 🛒 |
| review | 黄色 | ⭐ |
| reddit_post | 橙色 | 💬 |
| article | 绿色 | 📄 |
| error | 红色 | ⚠️ |

### 自定义样式

```tsx
<CitationBubble 
  number={1} 
  source={source}
  className="ml-2"  // 自定义间距
/>
```

---

## ✨ 最佳实践

1. **统一管理引用**: 使用 `CitationManager` 统一管理所有引用，避免重复
2. **提取函数**: 创建 `extractCitations()` 函数从报告数据中提取所有引用
3. **底部列表**: 在报告底部使用 `CitationList` 显示所有引用的详细信息
4. **内联引用**: 在关键数据点后使用 `CitedText` 或 `CitationBubble`
5. **数据结构**: 确保后端返回的数据包含 `_source` 字段

---

## 📚 更多资源

- [组件源码](./components/)
- [报告页面示例](./app/report/[taskId]/page.tsx)
- [API 类型定义](./lib/api.ts)

---

**版本**: 1.0.0  
**状态**: ✅ 生产就绪  
**更新时间**: 2026-01-13

