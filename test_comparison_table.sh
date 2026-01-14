#!/bin/bash

# 竞品对比表完善验证脚本
# 日期: 2026-01-14

echo "=========================================="
echo "竞品对比表完善验证"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数
PASS=0
FAIL=0

# 1. 检查后端 Prompt 更新
echo "1. 检查后端 Prompt 更新..."
if grep -q "痛点分析（pain_points）" backend/orchestrator/orchestrator.py && \
   grep -q "交付/售后（delivery_service）" backend/orchestrator/orchestrator.py && \
   grep -q "材质/稳定性（material_stability）" backend/orchestrator/orchestrator.py; then
    echo -e "${GREEN}✅ 后端 Prompt 已更新（包含3个新维度）${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ 后端 Prompt 未更新${NC}"
    ((FAIL++))
fi

# 2. 检查后端示例格式
echo "2. 检查后端示例格式..."
if grep -q '"pain_points": {{' backend/orchestrator/orchestrator.py && \
   grep -q '"delivery_service": {{' backend/orchestrator/orchestrator.py && \
   grep -q '"material_stability": {{' backend/orchestrator/orchestrator.py; then
    echo -e "${GREEN}✅ 后端示例格式正确${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ 后端示例格式不正确${NC}"
    ((FAIL++))
fi

# 3. 检查前端痛点分析组件
echo "3. 检查前端痛点分析组件..."
if grep -q "痛点分析" frontend/app/report/\[taskId\]/page.tsx && \
   grep -q "border-red-200 bg-red-50" frontend/app/report/\[taskId\]/page.tsx; then
    echo -e "${GREEN}✅ 前端痛点分析组件已添加（红色样式）${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ 前端痛点分析组件未添加${NC}"
    ((FAIL++))
fi

# 4. 检查前端交付/售后组件
echo "4. 检查前端交付/售后组件..."
if grep -q "交付/售后" frontend/app/report/\[taskId\]/page.tsx && \
   grep -q "border-blue-200 bg-blue-50" frontend/app/report/\[taskId\]/page.tsx; then
    echo -e "${GREEN}✅ 前端交付/售后组件已添加（蓝色样式）${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ 前端交付/售后组件未添加${NC}"
    ((FAIL++))
fi

# 5. 检查前端材质/稳定性组件
echo "5. 检查前端材质/稳定性组件..."
if grep -q "材质/稳定性" frontend/app/report/\[taskId\]/page.tsx && \
   grep -q "border-green-200 bg-green-50" frontend/app/report/\[taskId\]/page.tsx; then
    echo -e "${GREEN}✅ 前端材质/稳定性组件已添加（绿色样式）${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ 前端材质/稳定性组件未添加${NC}"
    ((FAIL++))
fi

# 6. 检查前端字段显示
echo "6. 检查前端字段显示..."
if grep -q "service.shipping" frontend/app/report/\[taskId\]/page.tsx && \
   grep -q "service.warranty" frontend/app/report/\[taskId\]/page.tsx && \
   grep -q "material.materials" frontend/app/report/\[taskId\]/page.tsx && \
   grep -q "material.weight_capacity" frontend/app/report/\[taskId\]/page.tsx; then
    echo -e "${GREEN}✅ 前端字段显示完整${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ 前端字段显示不完整${NC}"
    ((FAIL++))
fi

# 7. 检查引用气泡支持
echo "7. 检查引用气泡支持..."
if grep -A 20 "痛点分析" frontend/app/report/\[taskId\]/page.tsx | grep -q "CitationBubble" && \
   grep -A 30 "交付/售后" frontend/app/report/\[taskId\]/page.tsx | grep -q "CitationBubble" && \
   grep -A 30 "材质/稳定性" frontend/app/report/\[taskId\]/page.tsx | grep -q "CitationBubble"; then
    echo -e "${GREEN}✅ 引用气泡支持已添加${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ 引用气泡支持未添加${NC}"
    ((FAIL++))
fi

# 8. 检查文档
echo "8. 检查文档..."
if [ -f "COMPARISON_TABLE_ENHANCEMENT.md" ] && \
   [ -f "COMPARISON_TABLE_SUMMARY.md" ] && \
   [ -f "comparison_table_example.json" ]; then
    echo -e "${GREEN}✅ 文档已创建${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ 文档未创建${NC}"
    ((FAIL++))
fi

# 9. 检查后端服务
echo "9. 检查后端服务..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务运行中${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  后端服务未运行（需要手动启动）${NC}"
fi

# 10. 检查前端服务
echo "10. 检查前端服务..."
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端服务运行中${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  前端服务未运行（需要手动启动）${NC}"
fi

echo ""
echo "=========================================="
echo "验证结果"
echo "=========================================="
echo -e "通过: ${GREEN}${PASS}${NC}"
echo -e "失败: ${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！竞品对比表已完善！${NC}"
    echo ""
    echo "新增维度："
    echo "  ⚠️  痛点分析 - 识别竞品弱点"
    echo "  🚚 交付/售后 - 对比服务水平"
    echo "  🔧 材质/稳定性 - 评估产品质量"
    echo ""
    echo "从 4 个维度扩展到 7 个维度（+75%）"
    exit 0
else
    echo -e "${RED}❌ 有 ${FAIL} 项检查失败，请检查修改${NC}"
    exit 1
fi

