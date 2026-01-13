'use client'

import { useState, useRef, useEffect } from 'react'

/**
 * 引用来源数据结构
 */
export interface CitationSource {
  type: 'product_page' | 'review' | 'reddit_post' | 'article' | 'error'
  url: string
  brand?: string
  subreddit?: string
  domain?: string
  extracted_at: string
  data_points?: string[]
}

/**
 * 引用气泡组件属性
 */
interface CitationBubbleProps {
  /** 引用编号 */
  number: number
  /** 引用来源 */
  source: CitationSource
  /** 自定义样式 */
  className?: string
}

/**
 * 引用气泡组件
 * 
 * 显示一个可点击的引用编号，点击后展开详细信息
 */
export function CitationBubble({ number, source, className = '' }: CitationBubbleProps) {
  const [isOpen, setIsOpen] = useState(false)
  const popoverRef = useRef<HTMLDivElement>(null)

  // 点击外部关闭
  useEffect(() => {
    if (!isOpen) return

    const handleClickOutside = (event: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  // 根据来源类型获取图标和颜色
  const getSourceStyle = () => {
    switch (source.type) {
      case 'product_page':
        return { icon: '🛒', color: 'blue', label: '产品页' }
      case 'review':
        return { icon: '⭐', color: 'yellow', label: '评论' }
      case 'reddit_post':
        return { icon: '💬', color: 'orange', label: 'Reddit' }
      case 'article':
        return { icon: '📄', color: 'green', label: '文章' }
      case 'error':
        return { icon: '⚠️', color: 'red', label: '错误' }
      default:
        return { icon: '📌', color: 'gray', label: '来源' }
    }
  }

  const style = getSourceStyle()

  return (
    <span className={`relative inline-block ${className}`} ref={popoverRef}>
      {/* 引用编号气泡 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          inline-flex items-center justify-center
          w-5 h-5 text-xs font-semibold
          rounded-full cursor-pointer
          transition-all duration-200
          ${isOpen 
            ? `bg-${style.color}-600 text-white scale-110` 
            : `bg-${style.color}-100 text-${style.color}-700 hover:bg-${style.color}-200`
          }
        `}
        style={{
          backgroundColor: isOpen 
            ? `var(--color-${style.color}-600, #3b82f6)` 
            : `var(--color-${style.color}-100, #dbeafe)`,
          color: isOpen ? 'white' : `var(--color-${style.color}-700, #1e40af)`,
        }}
        title={`引用 ${number}: ${style.label}`}
      >
        {number}
      </button>

      {/* 引用详情弹窗 */}
      {isOpen && (
        <div
          className="absolute z-50 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 p-4"
          style={{ left: '50%', transform: 'translateX(-50%)' }}
        >
          {/* 箭头 */}
          <div
            className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-white border-l border-t border-gray-200 rotate-45"
          />

          {/* 内容 */}
          <div className="relative">
            {/* 标题 */}
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-200">
              <span className="text-xl">{style.icon}</span>
              <div className="flex-1">
                <div className="font-semibold text-gray-900">{style.label}</div>
                {source.brand && (
                  <div className="text-sm text-gray-600">{source.brand}</div>
                )}
                {source.subreddit && (
                  <div className="text-sm text-gray-600">{source.subreddit}</div>
                )}
                {source.domain && (
                  <div className="text-sm text-gray-600">{source.domain}</div>
                )}
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            {/* URL */}
            <div className="mb-3">
              <div className="text-xs text-gray-500 mb-1">来源链接</div>
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline break-all"
              >
                {source.url}
              </a>
            </div>

            {/* 数据点 */}
            {source.data_points && source.data_points.length > 0 && (
              <div className="mb-3">
                <div className="text-xs text-gray-500 mb-1">提取的数据</div>
                <div className="flex flex-wrap gap-1">
                  {source.data_points.map((point, idx) => (
                    <span
                      key={idx}
                      className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                    >
                      {point}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 提取时间 */}
            <div className="text-xs text-gray-500">
              提取时间: {new Date(source.extracted_at).toLocaleString('zh-CN')}
            </div>
          </div>
        </div>
      )}
    </span>
  )
}

