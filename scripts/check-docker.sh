#!/bin/bash

# ============================================
# Docker 环境检查脚本
# ============================================

echo "🔍 检查 Docker 环境..."
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo ""
    echo "请访问以下链接安装 Docker Desktop:"
    echo "https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker 已安装"
echo "   版本: $(docker --version)"
echo ""

# 检查 Docker daemon 是否运行
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon 未运行"
    echo ""
    echo "请执行以下操作:"
    echo "  1. 打开 Docker Desktop 应用"
    echo "  2. 等待菜单栏的 Docker 图标变为绿色"
    echo "  3. 重新运行此脚本"
    echo ""
    echo "macOS: 打开 /Applications/Docker.app"
    echo "Windows: 打开 Docker Desktop"
    exit 1
fi

echo "✅ Docker daemon 正在运行"
echo ""

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose 命令未找到，尝试使用 docker compose"
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose 未安装"
        exit 1
    fi
    echo "✅ Docker Compose 已安装 (docker compose)"
    echo "   版本: $(docker compose version)"
else
    echo "✅ Docker Compose 已安装"
    echo "   版本: $(docker-compose --version)"
fi

echo ""

# 检查运行中的容器
echo "📦 当前运行的容器:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ Docker 环境检查完成！"
echo ""
echo "下一步:"
echo "  运行: make dev"
echo "  或: docker-compose up -d"

