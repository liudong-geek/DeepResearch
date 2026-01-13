'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getResearchResult, pollResearchStatus, ResearchResult, ResearchStatus } from '@/lib/api'

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
                数据来源: <span className="font-semibold text-blue-600">{result.metadata.data_sources}</span> 个
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
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {result.competitors.length}
            </div>
            <div className="text-sm text-gray-600">竞品数量</div>
          </div>

          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {result.comparison_table?.sources?.length || result.metadata?.data_sources || 0}
            </div>
            <div className="text-sm text-gray-600">数据来源</div>
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

        {/* 行动计划 */}
        <ActionPlan data={result.action_plan} />

        {/* 数据来源 */}
        {result.comparison_table?.sources && result.comparison_table.sources.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">📚 数据来源</h2>
            <div className="space-y-3">
              {result.comparison_table.sources.map((source: any, idx: number) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900 mb-1">
                        {source.brand}
                      </div>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline break-all"
                      >
                        {source.url}
                      </a>
                      {source.data_points && source.data_points.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {source.data_points.map((point: string, i: number) => (
                            <span
                              key={i}
                              className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                            >
                              {point}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    {source.extracted_at && (
                      <div className="text-xs text-gray-500 ml-4 whitespace-nowrap">
                        {new Date(source.extracted_at).toLocaleString('zh-CN', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* 数据可信度说明 */}
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <div className="text-sm text-gray-700">
                <span className="font-semibold">💡 数据可信度说明：</span>
                所有数据均来自公开网页，遵守网站 robots.txt 规则，采用限速抓取。
                每个结论都可追溯到原始数据源，确保透明度和可审计性。
              </div>
            </div>
          </div>
        )}

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

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 竞品对比</h2>

      {/* 价格对比 */}
      {data.price_comparison && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">💰 价格对比</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data.price_comparison).map(([brand, info]: [string, any]) => {
              // 确保 price 是数字
              const price = typeof info.price === 'number'
                ? info.price
                : typeof info.price === 'string'
                  ? parseFloat(info.price)
                  : null

              return (
                <div key={brand} className="border border-gray-200 rounded-lg p-4">
                  <div className="font-semibold text-gray-900 mb-2">{brand}</div>
                  <div className="text-2xl font-bold text-blue-600 mb-2">
                    {price !== null && !isNaN(price) ? `$${price.toFixed(2)}` : info.price || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-600">{info.positioning}</div>
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
            {Object.entries(data.feature_comparison).map(([brand, features]: [string, any]) => (
              <div key={brand} className="border border-gray-200 rounded-lg p-4">
                <div className="font-semibold text-gray-900 mb-2">{brand}</div>
                <ul className="list-disc list-inside space-y-1">
                  {Array.isArray(features) && features.map((feature: string, idx: number) => (
                    <li key={idx} className="text-sm text-gray-700">{feature}</li>
                  ))}
                </ul>
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

