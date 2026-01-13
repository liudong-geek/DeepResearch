'use client'

import { CitationSource } from './CitationBubble'

/**
 * 引用来源列表组件属性
 */
interface CitationListProps {
  /** 引用来源列表 */
  sources: CitationSource[]
  /** 标题 */
  title?: string
  /** 自定义样式 */
  className?: string
}

/**
 * 引用来源列表组件
 * 
 * 在报告底部显示所有引用来源的详细信息
 */
export function CitationList({ 
  sources, 
  title = '📚 数据来源', 
  className = '' 
}: CitationListProps) {
  if (!sources || sources.length === 0) {
    return null
  }

  // 根据类型分组
  const groupedSources = sources.reduce((acc, source, idx) => {
    const type = source.type
    if (!acc[type]) {
      acc[type] = []
    }
    acc[type].push({ ...source, number: idx + 1 })
    return acc
  }, {} as Record<string, (CitationSource & { number: number })[]>)

  // 类型标签映射
  const typeLabels: Record<string, { icon: string; label: string; color: string }> = {
    product_page: { icon: '🛒', label: '产品页', color: 'blue' },
    review: { icon: '⭐', label: '评论', color: 'yellow' },
    reddit_post: { icon: '💬', label: 'Reddit 讨论', color: 'orange' },
    article: { icon: '📄', label: '测评文章', color: 'green' },
    error: { icon: '⚠️', label: '错误', color: 'red' },
  }

  return (
    <div className={`bg-white rounded-2xl shadow-xl p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">{title}</h2>

      {/* 统计信息 */}
      <div className="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="text-sm text-gray-600">
          总计 <span className="font-semibold text-gray-900">{sources.length}</span> 个数据来源
        </div>
        {Object.entries(groupedSources).map(([type, items]) => {
          const style = typeLabels[type] || { icon: '📌', label: type, color: 'gray' }
          return (
            <div key={type} className="text-sm text-gray-600">
              {style.icon} {style.label}: <span className="font-semibold text-gray-900">{items.length}</span>
            </div>
          )
        })}
      </div>

      {/* 按类型分组显示 */}
      <div className="space-y-6">
        {Object.entries(groupedSources).map(([type, items]) => {
          const style = typeLabels[type] || { icon: '📌', label: type, color: 'gray' }
          
          return (
            <div key={type}>
              {/* 类型标题 */}
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <span>{style.icon}</span>
                <span>{style.label}</span>
                <span className="text-sm font-normal text-gray-500">({items.length})</span>
              </h3>

              {/* 来源列表 */}
              <div className="space-y-3">
                {items.map((source) => (
                  <div
                    key={source.number}
                    className={`border-l-4 border-${style.color}-500 pl-4 py-2 bg-gray-50 rounded-r-lg`}
                    style={{ borderLeftColor: `var(--color-${style.color}-500, #3b82f6)` }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        {/* 引用编号 */}
                        <div className="flex items-center gap-2 mb-2">
                          <span
                            className="inline-flex items-center justify-center w-6 h-6 text-xs font-semibold rounded-full"
                            style={{
                              backgroundColor: `var(--color-${style.color}-100, #dbeafe)`,
                              color: `var(--color-${style.color}-700, #1e40af)`,
                            }}
                          >
                            {source.number}
                          </span>
                          {source.brand && (
                            <span className="font-semibold text-gray-900">{source.brand}</span>
                          )}
                          {source.subreddit && (
                            <span className="font-semibold text-gray-900">{source.subreddit}</span>
                          )}
                          {source.domain && (
                            <span className="font-semibold text-gray-900">{source.domain}</span>
                          )}
                        </div>

                        {/* URL */}
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:underline break-all block mb-2"
                        >
                          {source.url}
                        </a>

                        {/* 数据点 */}
                        {source.data_points && source.data_points.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {source.data_points.map((point, idx) => (
                              <span
                                key={idx}
                                className="text-xs bg-white text-gray-600 px-2 py-1 rounded border border-gray-200"
                              >
                                {point}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* 提取时间 */}
                      {source.extracted_at && (
                        <div className="text-xs text-gray-500 ml-4 whitespace-nowrap">
                          {new Date(source.extracted_at).toLocaleString('zh-CN', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* 数据可信度说明 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <div className="text-sm text-gray-700">
          <span className="font-semibold">💡 数据可信度说明：</span>
          所有数据均来自公开网页，遵守网站 robots.txt 规则，采用限速抓取。
          每个结论都可追溯到原始数据源，确保透明度和可审计性。
        </div>
      </div>
    </div>
  )
}

