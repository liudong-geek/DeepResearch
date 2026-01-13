'use client'

import { CitationBubble, CitationSource } from './CitationBubble'

/**
 * 带引用的文本组件属性
 */
interface CitedTextProps {
  /** 文本内容 */
  text: string
  /** 引用来源列表 */
  sources: CitationSource[]
  /** 自定义样式 */
  className?: string
}

/**
 * 带引用的文本组件
 * 
 * 在文本后面显示引用气泡
 * 
 * 示例:
 * <CitedText 
 *   text="Uplift 的价格为 $599"
 *   sources={[{ type: 'product_page', url: '...', brand: 'Uplift', ... }]}
 * />
 */
export function CitedText({ text, sources, className = '' }: CitedTextProps) {
  if (!sources || sources.length === 0) {
    return <span className={className}>{text}</span>
  }

  return (
    <span className={className}>
      {text}
      {sources.map((source, idx) => (
        <CitationBubble
          key={idx}
          number={idx + 1}
          source={source}
          className="ml-1"
        />
      ))}
    </span>
  )
}

/**
 * 带引用的段落组件属性
 */
interface CitedParagraphProps {
  /** 段落内容 */
  content: string
  /** 引用来源 */
  source?: CitationSource
  /** 自定义样式 */
  className?: string
}

/**
 * 带引用的段落组件
 * 
 * 在段落末尾显示引用气泡
 */
export function CitedParagraph({ content, source, className = '' }: CitedParagraphProps) {
  return (
    <p className={className}>
      {content}
      {source && (
        <CitationBubble
          number={1}
          source={source}
          className="ml-1"
        />
      )}
    </p>
  )
}

/**
 * 带引用的列表项组件属性
 */
interface CitedListItemProps {
  /** 列表项内容 */
  content: string
  /** 引用来源 */
  source?: CitationSource
  /** 自定义样式 */
  className?: string
}

/**
 * 带引用的列表项组件
 * 
 * 在列表项末尾显示引用气泡
 */
export function CitedListItem({ content, source, className = '' }: CitedListItemProps) {
  return (
    <li className={className}>
      {content}
      {source && (
        <CitationBubble
          number={1}
          source={source}
          className="ml-1"
        />
      )}
    </li>
  )
}

/**
 * 引用来源管理器
 * 
 * 用于管理多个引用来源，自动分配编号
 */
export class CitationManager {
  private sources: Map<string, CitationSource> = new Map()
  private counter = 0

  /**
   * 添加引用来源
   * @returns 引用编号
   */
  addSource(source: CitationSource): number {
    const key = `${source.type}-${source.url}`
    
    if (!this.sources.has(key)) {
      this.sources.set(key, source)
      this.counter++
    }
    
    return this.getSourceNumber(source)
  }

  /**
   * 获取引用编号
   */
  getSourceNumber(source: CitationSource): number {
    const key = `${source.type}-${source.url}`
    const entries = Array.from(this.sources.entries())
    const index = entries.findIndex(([k]) => k === key)
    return index + 1
  }

  /**
   * 获取所有引用来源
   */
  getAllSources(): CitationSource[] {
    return Array.from(this.sources.values())
  }

  /**
   * 清空所有引用
   */
  clear() {
    this.sources.clear()
    this.counter = 0
  }
}

