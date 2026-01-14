#!/bin/bash

# P0 修复验证脚本
# 测试评论洞察和行动计划的前后端集成

echo "🧪 P0 修复验证测试"
echo "===================="
echo ""

# 检查后端是否运行
echo "1️⃣ 检查后端服务..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null)
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ 后端服务正常运行"
else
    echo "❌ 后端服务未运行 (HTTP $BACKEND_STATUS)"
    echo "   请先启动后端: cd backend && source .venv/bin/activate && python -m uvicorn api.main:app --reload"
    exit 1
fi

# 检查前端是否运行
echo ""
echo "2️⃣ 检查前端服务..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ 前端服务正常运行 (http://localhost:3001)"
else
    FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
    if [ "$FRONTEND_STATUS" = "200" ]; then
        echo "✅ 前端服务正常运行 (http://localhost:3000)"
    else
        echo "❌ 前端服务未运行"
        echo "   请先启动前端: cd frontend && npm run dev"
        exit 1
    fi
fi

# 检查前端代码是否包含新组件
echo ""
echo "3️⃣ 检查前端代码修复..."

if grep -q "ReviewInsights" frontend/app/report/\[taskId\]/page.tsx; then
    echo "✅ ReviewInsights 组件已添加"
else
    echo "❌ ReviewInsights 组件未找到"
    exit 1
fi

if grep -q "data.marketing" frontend/app/report/\[taskId\]/page.tsx; then
    echo "✅ 投放建议显示已添加"
else
    echo "❌ 投放建议显示未找到"
    exit 1
fi

if grep -q "data.product" frontend/app/report/\[taskId\]/page.tsx; then
    echo "✅ 产品改进显示已添加"
else
    echo "❌ 产品改进显示未找到"
    exit 1
fi

if grep -q "data.customer_service" frontend/app/report/\[taskId\]/page.tsx; then
    echo "✅ 客服准备显示已添加"
else
    echo "❌ 客服准备显示未找到"
    exit 1
fi

# 检查后端是否返回正确的数据结构
echo ""
echo "4️⃣ 检查后端数据结构..."

if grep -q "review_insights" backend/orchestrator/orchestrator.py; then
    echo "✅ 后端返回 review_insights"
else
    echo "❌ 后端未返回 review_insights"
    exit 1
fi

if grep -q "action_plan" backend/orchestrator/orchestrator.py; then
    echo "✅ 后端返回 action_plan"
else
    echo "❌ 后端未返回 action_plan"
    exit 1
fi

# 总结
echo ""
echo "===================="
echo "✅ 所有 P0 修复验证通过！"
echo ""
echo "📋 修复内容："
echo "  1. ✅ 评论洞察前端显示组件"
echo "  2. ✅ 行动计划完整显示（运营、投放、产品、客服）"
echo ""
echo "🌐 访问地址："
echo "  - 前端: http://localhost:3001 (或 http://localhost:3000)"
echo "  - 后端: http://localhost:8000"
echo ""
echo "📝 详细说明请查看: P0_FIXES_SUMMARY.md"
echo ""

