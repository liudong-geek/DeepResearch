#!/bin/bash

# DeepResearch 开发环境启动脚本
# 同时启动前端和后端服务

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 启动 DeepResearch 开发环境                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查依赖
echo "🔍 检查依赖..."

# 检查 Python 虚拟环境
if [ ! -d "backend/.venv" ]; then
    echo "❌ Python 虚拟环境不存在"
    echo "   请运行: make local-setup"
    exit 1
fi

# 检查 Node.js
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Node.js 未安装"
    echo "   请安装: brew install node"
    exit 1
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  前端依赖未安装，正在安装..."
    cd frontend && npm install && cd ..
fi

echo "✅ 依赖检查完成"
echo ""

# 创建日志目录
mkdir -p logs

# 启动后端
echo "🔧 启动后端 API..."
cd backend
.venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "   后端 PID: $BACKEND_PID"
echo "   日志: logs/backend.log"

# 等待后端启动
echo "   等待后端启动..."
sleep 3

# 检查后端是否启动成功
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ 后端启动失败"
    echo "   查看日志: tail -f logs/backend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ 后端启动成功"
echo ""

# 启动前端
echo "🎨 启动前端..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   前端 PID: $FRONTEND_PID"
echo "   日志: logs/frontend.log"

# 等待前端启动
echo "   等待前端启动..."
sleep 5

echo "✅ 前端启动成功"
echo ""

# 显示服务信息
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ 服务已启动                                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 服务地址:"
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "📋 进程 ID:"
echo "   后端: $BACKEND_PID"
echo "   前端: $FRONTEND_PID"
echo ""
echo "📊 查看日志:"
echo "   后端: tail -f logs/backend.log"
echo "   前端: tail -f logs/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   或按 Ctrl+C"
echo ""

# 保存 PID 到文件
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

# 等待用户中断
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; rm -f logs/*.pid; echo '✅ 服务已停止'; exit 0" INT TERM

echo "💡 按 Ctrl+C 停止所有服务"
echo ""

# 持续显示日志
tail -f logs/backend.log logs/frontend.log

