#!/bin/bash

# ============================================
# Poetry 安装脚本
# ============================================

echo "📦 安装 Poetry..."
echo "================================"
echo ""

# 检查是否已安装
if command -v poetry &> /dev/null; then
    echo "✅ Poetry 已安装"
    poetry --version
    exit 0
fi

# 安装 Poetry
echo "⬇️  下载并安装 Poetry..."
curl -sSL https://install.python-poetry.org | python3 -

# 添加到 PATH
echo ""
echo "📝 添加 Poetry 到 PATH..."
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

echo ""
echo "================================"
echo "✅ Poetry 安装完成！"
echo ""
echo "版本信息:"
poetry --version
echo ""
echo "下一步:"
echo "  1. 重新加载 shell: source ~/.zshrc"
echo "  2. 或者重启终端"
echo "  3. 运行: cd backend && poetry install"

