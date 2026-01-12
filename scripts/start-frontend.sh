#!/bin/bash

# ============================================
# 前端启动脚本（本地开发）
# ============================================

set -e

echo "🚀 启动前端服务..."
echo "================================"
echo ""

# 进入前端目录
cd frontend

# 检查 pnpm
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm 未安装"
    echo ""
    echo "请先安装 pnpm:"
    echo "  npm install -g pnpm"
    echo ""
    exit 1
fi

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    pnpm install
fi

# 启动服务
echo ""
echo "================================"
echo "✅ 启动 Next.js 服务..."
echo ""
echo "🌐 应用: http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"
echo ""

pnpm dev

