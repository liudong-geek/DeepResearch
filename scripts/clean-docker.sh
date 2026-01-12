#!/bin/bash

# ============================================
# Docker 清理脚本
# ============================================

echo "🧹 清理 Docker 环境..."
echo "================================"
echo ""

# 停止所有容器
echo "🛑 停止所有容器..."
docker-compose down

# 删除所有容器
echo "🗑️  删除项目容器..."
docker-compose rm -f

# 清理构建缓存
echo "🧹 清理构建缓存..."
docker builder prune -f

# 清理未使用的镜像
echo "🧹 清理未使用的镜像..."
docker image prune -f

echo ""
echo "================================"
echo "✅ 清理完成！"
echo ""
echo "下一步:"
echo "  运行: make dev"

