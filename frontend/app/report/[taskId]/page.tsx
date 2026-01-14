'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getResearchResult, pollResearchStatus, ResearchResult, ResearchStatus } from '@/lib/api'
import { CitationList, CitationSource, CitationBubble } from '@/components/citations'

// 从报告数据中提取所有引用来源
function extractCitations(result: ResearchResult): CitationSource[] {
  const citations: CitationSource[] = []

  // 从 comparison_table.sources 提取
  if (result.comparison_table?.sources) {
    result.comparison_table.sources.forEach((source: any) => {
      if (source._source) {
        citations.push(source._source)
      } else {
        // 兼容旧格式
        citations.push({
          type: 'product_page',
          url: source.url || '',
          brand: source.brand,
          extracted_at: source.extracted_at || new Date().toISOString(),
          data_points: source.data_points,
        })
      }
    })
  }

  // 从 reddit_discussions 提取
  if (result.reddit_discussions) {
    result.reddit_discussions.forEach((post: any) => {
      if (post._source) {
        citations.push(post._source)
      }
    })
  }

  return citations
}

// 根据品牌名查找引用来源
function findSourceByBrand(sources: CitationSource[], brand: string): CitationSource | undefined {
  return sources.find(s =>
    s.brand?.toLowerCase() === brand.toLowerCase()
  )
}

export default function ReportPage() {
  const params = useParams()
  const router = useRouter()
  const taskId = params.taskId as string

  const [status, setStatus] = useState<ResearchStatus | null>(null)
  const [result, setResult] = useState<ResearchResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!taskId) return

    // 轮询状态
    pollResearchStatus(
      taskId,
      (newStatus) => {
        setStatus(newStatus)
      }
    )
      .then((finalResult) => {
        setResult(finalResult)
      })
      .catch((err) => {
        setError(err.message)
      })
  }, [taskId])

  // 加载中
  if (!result && !error) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">
              正在生成调研报告...
            </h1>

            {/* 进度条 */}
            {status && (
              <div className="space-y-4">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>{status.current_step}</span>
                  <span>{status.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-blue-600 h-4 rounded-full transition-all duration-500"
                    style={{ width: `${status.progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* 加载动画 */}
            <div className="mt-8 flex justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
          </div>
        </div>
      </main>
    )
  }

  // 错误
  if (error) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h1 className="text-3xl font-bold text-red-600 mb-4">调研失败</h1>
            <p className="text-gray-700 mb-6">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              返回首页
            </button>
          </div>
        </div>
      </main>
    )
  }

  // 显示结果
  if (!result) {
    return null
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* 标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📊 调研报告
          </h1>
          <p className="text-gray-600">
            {result.keyword} · {result.market} 市场 · {result.competitors.join(', ')}
          </p>

          {/* 数据质量指标 */}
          <div className="flex items-center justify-center gap-6 mt-4">
            {/* 置信度 */}
            {result.metadata?.confidence !== undefined && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">数据置信度:</span>
                <div className="flex items-center gap-1">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500"
                      style={{ width: `${result.metadata.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-green-600">
                    {(result.metadata.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            )}

            {/* 数据来源数量 */}
            {result.metadata?.data_sources !== undefined && (
              <div className="text-sm text-gray-600">
                数据来源: <span className="font-semibold text-blue-600">
                  {typeof result.metadata.data_sources === 'number'
                    ? result.metadata.data_sources
                    : (result.metadata.data_sources.products || 0) +
                      (result.metadata.data_sources.reviews || 0) +
                      (result.metadata.data_sources.reddit_posts || 0)
                  }
                </span> 个
              </div>
            )}

            {/* 数据新鲜度 */}
            {result.metadata?.generated_at && (
              <div className="text-sm text-gray-500">
                生成时间: {new Date(result.metadata.generated_at).toLocaleString('zh-CN')}
              </div>
            )}
          </div>
        </div>

        {/* 数据统计卡片 */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {result.competitors.length}
            </div>
            <div className="text-sm text-gray-600">竞品数量</div>
          </div>

          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {result.comparison_table?.sources?.length ||
               (typeof result.metadata?.data_sources === 'object'
                 ? result.metadata.data_sources.products
                 : result.metadata?.data_sources) || 0}
            </div>
            <div className="text-sm text-gray-600">产品数据</div>
          </div>

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

          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {result.metadata?.confidence ? (result.metadata.confidence * 100).toFixed(0) : 'N/A'}%
            </div>
            <div className="text-sm text-gray-600">置信度</div>
          </div>
        </div>

        {/* 效率对比 */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">⚡ 效率对比</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-3xl font-bold text-blue-600">
                {result.efficiency_comparison.manual_hours}h
              </div>
              <div className="text-sm text-gray-600 mt-2">人工耗时</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-3xl font-bold text-green-600">
                {typeof result.efficiency_comparison.tool_seconds === 'number'
                  ? result.efficiency_comparison.tool_seconds.toFixed(1)
                  : result.efficiency_comparison.tool_seconds || 'N/A'}s
              </div>
              <div className="text-sm text-gray-600 mt-2">工具耗时</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-3xl font-bold text-purple-600">
                {typeof result.efficiency_comparison.speedup === 'number'
                  ? result.efficiency_comparison.speedup.toFixed(0)
                  : result.efficiency_comparison.speedup || 'N/A'}x
              </div>
              <div className="text-sm text-gray-600 mt-2">提速倍数</div>
            </div>
          </div>
        </div>

        {/* 竞品对比表 */}
        <ComparisonTable data={result.comparison_table} />

        {/* 评论洞察 */}
        {result.review_insights && (
          <ReviewInsights data={result.review_insights} />
        )}

        {/* 行动计划 */}
        <ActionPlan data={result.action_plan} />

        {/* Reddit 讨论 */}
        {result.reddit_discussions && result.reddit_discussions.length > 0 && (
          <RedditDiscussions data={result.reddit_discussions} />
        )}

        {/* 数据来源 - 使用新的 CitationList 组件 */}
        <CitationList sources={extractCitations(result)} className="mb-6" />

        {/* 返回按钮 */}
        <div className="text-center mt-8">
          <button
            onClick={() => router.push('/')}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            返回首页
          </button>
        </div>
      </div>
    </main>
  )
}

// 竞品对比表组件
function ComparisonTable({ data }: { data: any }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 竞品对比</h2>
        <p className="text-gray-500">暂无数据</p>
      </div>
    )
  }

  // 提取引用来源
  const sources: CitationSource[] = []
  if (data.sources && Array.isArray(data.sources)) {
    data.sources.forEach((source: any, idx: number) => {
      sources.push({
        type: 'product_page',
        url: source.url || source.source_url || '',
        brand: source.brand,
        extracted_at: source.extracted_at || new Date().toISOString(),
        data_points: source.data_points || ['price', 'features'],
      })
    })
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 竞品对比</h2>

      {/* 价格对比 */}
      {data.price_comparison && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">💰 价格对比</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data.price_comparison).map(([brand, info]: [string, any], idx: number) => {
              // 确保 price 是数字
              const price = typeof info.price === 'number'
                ? info.price
                : typeof info.price === 'string'
                  ? parseFloat(info.price)
                  : null

              // 查找对应的引用来源
              const source = findSourceByBrand(sources, brand)

              // 检查是否有价格警告（从 positioning 中提取）
              const hasWarning = info.positioning && (
                info.positioning.includes('价格异常') ||
                info.positioning.includes('需人工核实') ||
                info.positioning.includes('需验证')
              )

              return (
                <div key={brand} className={`border rounded-lg p-4 ${hasWarning ? 'border-yellow-300 bg-yellow-50' : 'border-gray-200'}`}>
                  <div className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    {brand}
                    {source && (
                      <CitationBubble
                        number={sources.indexOf(source) + 1}
                        source={source}
                      />
                    )}
                  </div>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="text-2xl font-bold text-blue-600">
                      {price !== null && !isNaN(price) ? `$${price.toFixed(2)}` : info.price || 'N/A'}
                    </div>
                    {hasWarning && (
                      <span className="text-yellow-600 text-sm" title="价格需要人工验证">
                        ⚠️
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-600 mb-2">{info.positioning}</div>
                  {hasWarning && source && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:text-blue-800 underline"
                    >
                      点击验证价格 →
                    </a>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 功能对比 */}
      {data.feature_comparison && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">✨ 功能对比</h3>
          <div className="space-y-4">
            {Object.entries(data.feature_comparison).map(([brand, features]: [string, any]) => {
              // 查找对应的引用来源
              const source = findSourceByBrand(sources, brand)

              return (
                <div key={brand} className="border border-gray-200 rounded-lg p-4">
                  <div className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    {brand}
                    {source && (
                      <CitationBubble
                        number={sources.indexOf(source) + 1}
                        source={source}
                      />
                    )}
                  </div>
                  <ul className="list-disc list-inside space-y-1">
                    {Array.isArray(features) && features.map((feature: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-700">{feature}</li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 痛点分析 */}
      {data.pain_points && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">⚠️ 痛点分析</h3>
          <div className="space-y-4">
            {Object.entries(data.pain_points).map(([brand, painPoints]: [string, any]) => {
              const source = findSourceByBrand(sources, brand)

              return (
                <div key={brand} className="border border-red-200 bg-red-50 rounded-lg p-4">
                  <div className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    {brand}
                    {source && (
                      <CitationBubble
                        number={sources.indexOf(source) + 1}
                        source={source}
                      />
                    )}
                  </div>
                  <ul className="list-disc list-inside space-y-1">
                    {Array.isArray(painPoints) && painPoints.map((point: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-700">{point}</li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 交付/售后 */}
      {data.delivery_service && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">🚚 交付/售后</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data.delivery_service).map(([brand, service]: [string, any]) => {
              const source = findSourceByBrand(sources, brand)

              return (
                <div key={brand} className="border border-blue-200 bg-blue-50 rounded-lg p-4">
                  <div className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    {brand}
                    {source && (
                      <CitationBubble
                        number={sources.indexOf(source) + 1}
                        source={source}
                      />
                    )}
                  </div>
                  <div className="space-y-2 text-sm">
                    {service.shipping && (
                      <div className="flex items-start gap-2">
                        <span className="text-gray-600 font-medium min-w-[80px]">发货时间:</span>
                        <span className="text-gray-700">{service.shipping}</span>
                      </div>
                    )}
                    {service.warranty && (
                      <div className="flex items-start gap-2">
                        <span className="text-gray-600 font-medium min-w-[80px]">保修政策:</span>
                        <span className="text-gray-700">{service.warranty}</span>
                      </div>
                    )}
                    {service.return_policy && (
                      <div className="flex items-start gap-2">
                        <span className="text-gray-600 font-medium min-w-[80px]">退货政策:</span>
                        <span className="text-gray-700">{service.return_policy}</span>
                      </div>
                    )}
                    {service.assembly && (
                      <div className="flex items-start gap-2">
                        <span className="text-gray-600 font-medium min-w-[80px]">组装要求:</span>
                        <span className="text-gray-700">{service.assembly}</span>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 材质/稳定性 */}
      {data.material_stability && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">🔧 材质/稳定性</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data.material_stability).map(([brand, material]: [string, any]) => {
              const source = findSourceByBrand(sources, brand)

              return (
                <div key={brand} className="border border-green-200 bg-green-50 rounded-lg p-4">
                  <div className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    {brand}
                    {source && (
                      <CitationBubble
                        number={sources.indexOf(source) + 1}
                        source={source}
                      />
                    )}
                  </div>
                  <div className="space-y-2 text-sm">
                    {material.materials && (
                      <div className="flex items-start gap-2">
                        <span className="text-gray-600 font-medium min-w-[80px]">材质:</span>
                        <span className="text-gray-700">{material.materials}</span>
                      </div>
                    )}
                    {material.weight_capacity && (
                      <div className="flex items-start gap-2">
                        <span className="text-gray-600 font-medium min-w-[80px]">承重能力:</span>
                        <span className="text-gray-700">{material.weight_capacity}</span>
                      </div>
                    )}
                    {material.stability && (
                      <div className="flex items-start gap-2">
                        <span className="text-gray-600 font-medium min-w-[80px]">稳定性:</span>
                        <span className="text-gray-700">{material.stability}</span>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 原始数据（折叠） */}
      <details className="mt-4">
        <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900">
          查看原始数据
        </summary>
        <pre className="mt-2 bg-gray-50 p-4 rounded-lg overflow-auto text-xs">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  )
}

// Reddit 讨论组件
function RedditDiscussions({ data }: { data: any[] }) {
  if (!data || data.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">💬 Reddit 讨论</h2>

      <div className="space-y-4">
        {data.slice(0, 5).map((post: any, idx: number) => {
          // 提取引用来源
          const source: CitationSource | undefined = post._source ? post._source : undefined

          return (
            <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              {/* 标题 */}
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900 flex-1 flex items-center gap-2">
                  {post.title}
                  {source && (
                    <CitationBubble
                      number={idx + 1}
                      source={source}
                    />
                  )}
                </h3>
                {post.score !== undefined && (
                  <div className="flex items-center gap-1 ml-4">
                    <span className="text-orange-500">⬆</span>
                    <span className="text-sm font-semibold text-gray-700">{post.score}</span>
                  </div>
                )}
              </div>

            {/* 内容预览 */}
            {post.content && (
              <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                {post.content}
              </p>
            )}

            {/* 元信息 */}
            <div className="flex items-center gap-4 text-xs text-gray-500">
              {post.subreddit && (
                <span className="flex items-center gap-1">
                  <span>📍</span>
                  <span>r/{post.subreddit}</span>
                </span>
              )}
              {post.author && (
                <span className="flex items-center gap-1">
                  <span>👤</span>
                  <span>u/{post.author}</span>
                </span>
              )}
              {post.num_comments !== undefined && (
                <span className="flex items-center gap-1">
                  <span>💬</span>
                  <span>{post.num_comments} 评论</span>
                </span>
              )}
              {post.url && (
                <a
                  href={post.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline ml-auto"
                >
                  查看原帖 →
                </a>
              )}
            </div>
            </div>
          )
        })}
      </div>

      {data.length > 5 && (
        <div className="mt-4 text-center text-sm text-gray-500">
          还有 {data.length - 5} 个讨论未显示
        </div>
      )}
    </div>
  )
}

// 行动计划组件
function ActionPlan({ data }: { data: any }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">🎯 行动计划</h2>
        <p className="text-gray-500">暂无数据</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">🎯 行动计划</h2>

      {/* 运营建议 */}
      {data.operations && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">📈 运营建议</h3>
          <div className="space-y-3">
            {data.operations.pricing_strategy && (
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                <div className="font-medium text-gray-900 mb-1">定价策略</div>
                <div className="text-sm text-gray-700">{data.operations.pricing_strategy}</div>
              </div>
            )}
            {data.operations.launch_strategy && (
              <div className="bg-green-50 border-l-4 border-green-500 p-4">
                <div className="font-medium text-gray-900 mb-1">上新策略</div>
                <div className="text-sm text-gray-700">{data.operations.launch_strategy}</div>
              </div>
            )}
            {data.operations.pdp_recommendations && Array.isArray(data.operations.pdp_recommendations) && (
              <div className="bg-purple-50 border-l-4 border-purple-500 p-4">
                <div className="font-medium text-gray-900 mb-2">产品页建议</div>
                <ul className="list-disc list-inside space-y-1">
                  {data.operations.pdp_recommendations.map((rec: string, idx: number) => (
                    <li key={idx} className="text-sm text-gray-700">{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 投放建议 */}
      {data.marketing && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">🎯 投放建议</h3>
          <div className="space-y-3">
            {data.marketing.target_audience && (
              <div className="bg-orange-50 border-l-4 border-orange-500 p-4">
                <div className="font-medium text-gray-900 mb-1">目标受众</div>
                <div className="text-sm text-gray-700">{data.marketing.target_audience}</div>
              </div>
            )}
            {data.marketing.creative_direction && Array.isArray(data.marketing.creative_direction) && (
              <div className="bg-pink-50 border-l-4 border-pink-500 p-4">
                <div className="font-medium text-gray-900 mb-2">素材方向</div>
                <ul className="list-disc list-inside space-y-1">
                  {data.marketing.creative_direction.map((item: string, idx: number) => (
                    <li key={idx} className="text-sm text-gray-700">{item}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.marketing.copy_direction && Array.isArray(data.marketing.copy_direction) && (
              <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
                <div className="font-medium text-gray-900 mb-2">文案方向</div>
                <ul className="list-disc list-inside space-y-1">
                  {data.marketing.copy_direction.map((item: string, idx: number) => (
                    <li key={idx} className="text-sm text-gray-700">{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 产品改进 */}
      {data.product && data.product.improvements && Array.isArray(data.product.improvements) && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">🔧 产品改进建议</h3>
          <div className="bg-red-50 border-l-4 border-red-500 p-4">
            <div className="font-medium text-gray-900 mb-2">Top 5 改进点</div>
            <ol className="list-decimal list-inside space-y-2">
              {data.product.improvements.map((item: string, idx: number) => (
                <li key={idx} className="text-sm text-gray-700">{item}</li>
              ))}
            </ol>
          </div>
        </div>
      )}

      {/* 客服准备 */}
      {data.customer_service && data.customer_service.faq && Array.isArray(data.customer_service.faq) && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">💬 客服准备</h3>
          <div className="space-y-3">
            {data.customer_service.faq.map((item: any, idx: number) => (
              <div key={idx} className="bg-teal-50 border-l-4 border-teal-500 p-4">
                <div className="font-medium text-gray-900 mb-1">Q: {item.question}</div>
                <div className="text-sm text-gray-700">A: {item.answer}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 原始数据（折叠） */}
      <details className="mt-4">
        <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900">
          查看原始数据
        </summary>
        <pre className="mt-2 bg-gray-50 p-4 rounded-lg overflow-auto text-xs">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  )
}

// 评论洞察组件
function ReviewInsights({ data }: { data: any }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">⭐ 评论洞察</h2>
        <p className="text-gray-500">暂无数据</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">⭐ 评论洞察</h2>

        {/* 数据来源 */}
        {data._sources && Array.isArray(data._sources) && data._sources.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">数据来源:</span>
            <div className="flex gap-2">
              {data._sources
                .filter((source: any) => source.type === 'trustpilot_reviews')
                .map((source: any, idx: number) => (
                  <a
                    key={idx}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs hover:bg-blue-100 transition-colors"
                    title={`${source.brand} - ${source.review_count} 条评论，平均 ${source.overall_rating} 星`}
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    {source.brand} Trustpilot
                  </a>
                ))}
            </div>
          </div>
        )}
      </div>

      {/* 元数据统计 */}
      {data._metadata && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex gap-6 text-sm text-gray-600">
            <div>
              <span className="font-medium">分析评论数:</span> {data._metadata.total_reviews_analyzed || 0}
            </div>
            {data._metadata.brands_analyzed && data._metadata.brands_analyzed.length > 0 && (
              <div>
                <span className="font-medium">品牌:</span> {data._metadata.brands_analyzed.join(', ')}
              </div>
            )}
            {data._metadata.total_reddit_posts > 0 && (
              <div>
                <span className="font-medium">Reddit 讨论:</span> {data._metadata.total_reddit_posts}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 情感分布 */}
      {data.sentiment_distribution && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">📊 情感分布</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-green-600">
                {data.sentiment_distribution.positive || 0}
              </div>
              <div className="text-sm text-gray-600 mt-1">正面评论</div>
              <div className="text-xs text-gray-500 mt-1">
                {data.sentiment_distribution.positive_percentage?.toFixed(1) || 0}%
              </div>
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-gray-600">
                {data.sentiment_distribution.neutral || 0}
              </div>
              <div className="text-sm text-gray-600 mt-1">中性评论</div>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-red-600">
                {data.sentiment_distribution.negative || 0}
              </div>
              <div className="text-sm text-gray-600 mt-1">负面评论</div>
              <div className="text-xs text-gray-500 mt-1">
                {data.sentiment_distribution.negative_percentage?.toFixed(1) || 0}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 主题标签 */}
      {data.topics && Array.isArray(data.topics) && data.topics.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">🏷️ 主题标签</h3>
          <div className="flex flex-wrap gap-2">
            {data.topics.map((topic: any, idx: number) => {
              const sentimentColor =
                topic.sentiment === 'positive' ? 'bg-green-100 text-green-800 border-green-300' :
                topic.sentiment === 'negative' ? 'bg-red-100 text-red-800 border-red-300' :
                topic.sentiment === 'mixed' ? 'bg-yellow-100 text-yellow-800 border-yellow-300' :
                'bg-gray-100 text-gray-800 border-gray-300'

              return (
                <div
                  key={idx}
                  className={`px-3 py-2 rounded-lg border ${sentimentColor} text-sm`}
                >
                  <span className="font-medium">{topic.name}</span>
                  <span className="ml-2 text-xs opacity-75">
                    ({topic.count || 0})
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 正面洞察 */}
      {data.positive_insights && Array.isArray(data.positive_insights) && data.positive_insights.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">👍 正面洞察 (Top 5)</h3>
          <div className="space-y-3">
            {data.positive_insights.map((insight: any, idx: number) => (
              <div key={idx} className="bg-green-50 border-l-4 border-green-500 p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="font-medium text-gray-900">
                    {insight.topic || `洞察 ${idx + 1}`}
                  </div>
                  {insight.count && (
                    <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">
                      {insight.count} 次提及
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-700 mb-2">{insight.summary}</div>
                {insight.examples && Array.isArray(insight.examples) && insight.examples.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {insight.examples.map((example: string, exIdx: number) => (
                      <div key={exIdx} className="text-xs text-gray-600 italic pl-3 border-l-2 border-green-300">
                        "{example}"
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 负面洞察 */}
      {data.negative_insights && Array.isArray(data.negative_insights) && data.negative_insights.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">👎 负面洞察 (Top 5)</h3>
          <div className="space-y-3">
            {data.negative_insights.map((insight: any, idx: number) => (
              <div key={idx} className="bg-red-50 border-l-4 border-red-500 p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="font-medium text-gray-900">
                    {insight.topic || `洞察 ${idx + 1}`}
                  </div>
                  {insight.count && (
                    <span className="text-xs bg-red-200 text-red-800 px-2 py-1 rounded">
                      {insight.count} 次提及
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-700 mb-2">{insight.summary}</div>
                {insight.examples && Array.isArray(insight.examples) && insight.examples.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {insight.examples.map((example: string, exIdx: number) => (
                      <div key={exIdx} className="text-xs text-gray-600 italic pl-3 border-l-2 border-red-300">
                        "{example}"
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 原始数据（折叠） */}
      <details className="mt-4">
        <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900">
          查看原始数据
        </summary>
        <pre className="mt-2 bg-gray-50 p-4 rounded-lg overflow-auto text-xs">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  )
}

