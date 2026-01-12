import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'DeepResearch - 竞品调研智能体',
  description: '基于 MCP 的自动化竞品调研系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="font-sans">{children}</body>
    </html>
  )
}

