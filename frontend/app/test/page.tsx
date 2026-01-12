'use client'

import { useState } from 'react'

export default function TestPage() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const testAPI = async () => {
    setLoading(true)
    setResult('测试中...')

    try {
      // 测试健康检查
      const healthResponse = await fetch('http://localhost:8001/api/health')
      const healthData = await healthResponse.json()
      
      setResult(prev => prev + '\n\n✅ 健康检查成功:\n' + JSON.stringify(healthData, null, 2))

      // 测试启动调研
      const researchResponse = await fetch('http://localhost:8001/api/research/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keyword: 'standing desk',
          market: 'US',
          competitors: ['Uplift', 'Vari']
        }),
      })

      if (!researchResponse.ok) {
        throw new Error(`HTTP ${researchResponse.status}: ${researchResponse.statusText}`)
      }

      const researchData = await researchResponse.json()
      setResult(prev => prev + '\n\n✅ 启动调研成功:\n' + JSON.stringify(researchData, null, 2))

    } catch (error: any) {
      setResult(prev => prev + '\n\n❌ 错误:\n' + error.message)
      console.error('API 测试失败:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">API 测试页面</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <button
            onClick={testAPI}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? '测试中...' : '测试 API'}
          </button>
        </div>

        {result && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">测试结果</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
              {result}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

