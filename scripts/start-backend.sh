#!/bin/bash

# ============================================
# 后端启动脚本（本地开发）
# ============================================

set -e

echo "🚀 启动后端服务..."
echo "================================"
echo ""

# 进入后端目录
cd backend

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 启动服务
echo ""
echo "================================"
echo "✅ 启动 FastAPI 服务..."
echo ""
echo "📡 API: http://localhost:8000"
echo "📚 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"
echo ""

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

