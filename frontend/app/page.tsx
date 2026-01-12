'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { startResearch } from '@/lib/api'

export default function Home() {
  const router = useRouter()
  const [competitors, setCompetitors] = useState<string[]>([])
  const [customCompetitor, setCustomCompetitor] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const availableCompetitors = ['Uplift', 'Jarvis', 'Vari', 'Autonomous']

  const toggleCompetitor = (competitor: string) => {
    setCompetitors(prev =>
      prev.includes(competitor)
        ? prev.filter(c => c !== competitor)
        : [...prev, competitor]
    )
  }

  const addCustomCompetitor = () => {
    if (customCompetitor && !competitors.includes(customCompetitor)) {
      setCompetitors([...competitors, customCompetitor])
      setCustomCompetitor('')
    }
  }

  const handleStartResearch = async () => {
    if (competitors.length === 0) {
      setError('请至少选择一个竞品')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // 调用后端 API
      const response = await startResearch({
        keyword: 'standing desk',
        market: 'US',
        competitors: competitors,
      })

      // 跳转到报告页面
      router.push(`/report/${response.task_id}`)
    } catch (err: any) {
      setError(err.message || '启动调研失败')
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* 标题 */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            DeepResearch
          </h1>
          <p className="text-xl text-gray-600">
            竞品调研智能体 - 基于 MCP 的自动化市场洞察
          </p>
        </div>

        {/* 输入表单 */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* 产品关键词 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              产品关键词
            </label>
            <input
              type="text"
              value="standing desk"
              disabled
              className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
            />
          </div>

          {/* 目标市场 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              目标市场
            </label>
            <input
              type="text"
              value="US"
              disabled
              className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
            />
          </div>

          {/* 竞品选择 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              选择竞品（至少1个）
            </label>
            <div className="grid grid-cols-2 gap-3 mb-4">
              {availableCompetitors.map(competitor => (
                <button
                  key={competitor}
                  onClick={() => toggleCompetitor(competitor)}
                  className={`px-4 py-3 rounded-lg border-2 transition-all ${
                    competitors.includes(competitor)
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                  }`}
                >
                  {competitor}
                </button>
              ))}
            </div>

            {/* 自定义竞品 */}
            <div className="flex gap-2">
              <input
                type="text"
                value={customCompetitor}
                onChange={e => setCustomCompetitor(e.target.value)}
                placeholder="添加自定义竞品..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                onKeyPress={e => e.key === 'Enter' && addCustomCompetitor()}
              />
              <button
                onClick={addCustomCompetitor}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                添加
              </button>
            </div>
          </div>

          {/* 已选择的竞品 */}
          {competitors.length > 0 && (
            <div className="mb-6">
              <p className="text-sm font-medium text-gray-700 mb-2">
                已选择 {competitors.length} 个竞品：
              </p>
              <div className="flex flex-wrap gap-2">
                {competitors.map(competitor => (
                  <span
                    key={competitor}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-2"
                  >
                    {competitor}
                    <button
                      onClick={() => toggleCompetitor(competitor)}
                      className="hover:text-blue-900"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 错误提示 */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          {/* 开始按钮 */}
          <button
            onClick={handleStartResearch}
            disabled={competitors.length === 0 || loading}
            className="w-full py-4 bg-blue-600 text-white rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                启动中...
              </>
            ) : (
              '开始调研'
            )}
          </button>
        </div>

        {/* 功能说明 */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="font-semibold text-gray-900 mb-2">📊 竞品对比</h3>
            <p className="text-sm text-gray-600">
              自动抓取产品页，对比价格、卖点、材质、稳定性
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="font-semibold text-gray-900 mb-2">⭐ 评论洞察</h3>
            <p className="text-sm text-gray-600">
              分析用户评论，提取主题标签、正负面要点
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="font-semibold text-gray-900 mb-2">🔗 引用溯源</h3>
            <p className="text-sm text-gray-600">
              每个结论可追溯到原始数据源，确保可信度
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

