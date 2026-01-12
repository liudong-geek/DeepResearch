#!/bin/bash

# ============================================
# 后端测试脚本
# ============================================

set -e

echo "🧪 DeepResearch 后端测试"
echo "================================"
echo ""

cd backend

# 检查 Poetry
if ! command -v poetry &> /dev/null; then
    echo "❌ 错误: 未安装 Poetry"
    echo "请运行: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "✅ Poetry 已安装"
echo ""

# 安装依赖
echo "📦 安装依赖..."
poetry install
echo "✅ 依赖安装完成"
echo ""

# 运行测试
echo "🧪 运行测试..."
poetry run pytest tests/test_mcp_server.py -v
echo ""

echo "================================"
echo "✅ 测试完成！"

