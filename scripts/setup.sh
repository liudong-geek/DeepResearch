#!/bin/bash

# ============================================
# DeepResearch 项目初始化脚本
# ============================================

set -e  # 遇到错误立即退出

echo "🚀 DeepResearch 项目初始化"
echo "================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    echo "请访问 https://www.docker.com/get-started 安装 Docker"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 创建 .env 文件
if [ ! -f .env ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "✅ .env 文件已创建"
    echo ""
    echo "⚠️  重要提示："
    echo "   请编辑 .env 文件，填入你的 OPENAI_API_KEY"
    echo "   vim .env"
    echo ""
else
    echo "⚠️  .env 文件已存在，跳过创建"
    echo ""
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p backend/logs
mkdir -p backend/.cache
echo "✅ 目录创建完成"
echo ""

# 启动数据库服务
echo "🐳 启动数据库服务..."
docker-compose up -d postgres redis
echo "✅ 数据库服务已启动"
echo ""

# 等待数据库就绪
echo "⏳ 等待数据库就绪..."
sleep 5
echo "✅ 数据库已就绪"
echo ""

echo "================================"
echo "✅ 项目初始化完成！"
echo ""
echo "下一步："
echo "  1. 编辑 .env 文件，填入 API Keys"
echo "  2. 运行 'make dev' 启动开发环境"
echo "  3. 访问 http://localhost:3000"
echo ""

