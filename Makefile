.PHONY: help setup dev dev-bg stop logs test lint format clean deploy db-migrate db-reset
.PHONY: local-setup local-dev local-test local-backend local-frontend local-test-e2e

# ============================================
# 默认目标：显示帮助
# ============================================
help:  ## 显示帮助信息
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║         DeepResearch - 竞品调研智能体                          ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 快速开始（推荐）:"
	@echo "  make local-setup    # 初始化本地开发环境"
	@echo "  make local-test-e2e # 运行端到端测试（最快体验）"
	@echo "  make local-backend  # 启动后端 API"
	@echo ""
	@echo "📋 所有可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 提示:"
	@echo "  - 本地开发（推荐）: make local-* 命令"
	@echo "  - Docker 开发: make dev / make dev-bg"
	@echo "  - 查看状态: cat CURRENT_STATUS.md"

# ============================================
# 本地开发环境（推荐，当前可用）
# ============================================
local-setup:  ## 🚀 初始化本地开发环境（推荐）
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  🚀 初始化 DeepResearch 本地开发环境                           ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📝 步骤 1/4: 检查环境变量文件"
	@if [ ! -f .env ]; then \
		cp .env.example .env 2>/dev/null || echo "⚠️  .env.example 不存在"; \
		echo "✅ 已创建 .env 文件"; \
	else \
		echo "✅ .env 文件已存在"; \
	fi
	@echo ""
	@echo "📦 步骤 2/4: 安装后端依赖"
	@cd backend && \
		if [ ! -d .venv ]; then \
			python3 -m venv .venv; \
			echo "✅ 创建虚拟环境"; \
		fi && \
		.venv/bin/pip install -r requirements.txt && \
		echo "✅ 后端依赖安装完成"
	@echo ""
	@echo "🎭 步骤 3/4: 安装 Playwright 浏览器"
	@cd backend && .venv/bin/playwright install chromium && \
		echo "✅ Playwright 浏览器安装完成"
	@echo ""
	@echo "📦 步骤 4/4: 检查前端依赖（可选）"
	@if command -v node >/dev/null 2>&1; then \
		echo "✅ Node.js 已安装: $$(node --version)"; \
		if [ ! -d frontend/node_modules ]; then \
			echo "📦 安装前端依赖..."; \
			cd frontend && npm install; \
		else \
			echo "✅ 前端依赖已安装"; \
		fi; \
	else \
		echo "⚠️  Node.js 未安装，跳过前端依赖"; \
		echo "   如需前端，请安装: brew install node"; \
	fi
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  ✅ 本地开发环境初始化完成！                                    ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "⚠️  重要提示："
	@echo "   1. 请编辑 .env 文件，配置 LLM API Key:"
	@echo "      LLM_PROVIDER=qwen"
	@echo "      LLM_API_KEY=your-api-key"
	@echo ""
	@echo "🚀 下一步："
	@echo "   make local-test-e2e  # 运行端到端测试（最快体验）"
	@echo "   make local-backend   # 启动后端 API"
	@echo "   make local-dev       # 启动前后端（需要 Node.js）"

local-test-e2e:  ## 🧪 运行端到端测试（最快体验，推荐）
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  🧪 运行端到端测试 - 完整功能演示                              ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@if [ -z "$$LLM_API_KEY" ]; then \
		echo "⚠️  环境变量 LLM_API_KEY 未设置"; \
		echo "   正在从 .env 文件读取..."; \
		export $$(cat .env | grep -v '^#' | xargs); \
	fi
	@cd backend && \
		export LLM_PROVIDER=$${LLM_PROVIDER:-qwen} && \
		export LLM_API_KEY=$${LLM_API_KEY} && \
		.venv/bin/python ../test_end_to_end.py
	@echo ""
	@echo "📊 查看完整报告:"
	@echo "   cat backend/test_report.json | python3 -m json.tool | less"

local-backend:  ## 🔧 启动后端 API 服务
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  🔧 启动后端 API 服务                                          ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📍 服务地址:"
	@echo "   后端 API: http://localhost:8000"
	@echo "   API 文档: http://localhost:8000/docs"
	@echo ""
	@echo "💡 按 Ctrl+C 停止服务"
	@echo ""
	@cd backend && .venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

local-frontend:  ## 🎨 启动前端服务（需要 Node.js）
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  🎨 启动前端服务                                               ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@if ! command -v node >/dev/null 2>&1; then \
		echo "❌ Node.js 未安装"; \
		echo "   请安装: brew install node"; \
		exit 1; \
	fi
	@echo "📍 前端地址: http://localhost:3000"
	@echo ""
	@cd frontend && npm run dev

local-dev:  ## 🚀 启动前后端服务（需要 Node.js）
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  🚀 启动完整开发环境                                           ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@if ! command -v node >/dev/null 2>&1; then \
		echo "❌ Node.js 未安装，只启动后端"; \
		echo "   如需前端，请安装: brew install node"; \
		make local-backend; \
	else \
		./start_dev.sh; \
	fi

local-test:  ## 🧪 运行所有本地测试
	@echo "🧪 运行本地测试..."
	@cd backend && .venv/bin/python ../test_qwen.py
	@echo ""
	@cd backend && .venv/bin/python ../test_all_scrapers.py

local-status:  ## 📊 查看项目状态
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  📊 DeepResearch 项目状态                                      ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🐍 Python 环境:"
	@if [ -d backend/.venv ]; then \
		echo "  ✅ 虚拟环境: backend/.venv"; \
		echo "  版本: $$(backend/.venv/bin/python --version 2>&1)"; \
	else \
		echo "  ❌ 虚拟环境未创建"; \
	fi
	@echo ""
	@echo "📦 Node.js 环境:"
	@if command -v node >/dev/null 2>&1; then \
		echo "  ✅ Node.js: $$(node --version 2>&1)"; \
		if [ -d frontend/node_modules ]; then \
			echo "  ✅ 前端依赖已安装"; \
		else \
			echo "  ⚠️  前端依赖未安装"; \
		fi; \
	else \
		echo "  ❌ Node.js 未安装"; \
	fi
	@echo ""
	@echo "🔑 环境变量:"
	@if [ -f .env ]; then \
		echo "  ✅ .env 文件存在"; \
		if grep -q "LLM_API_KEY=sk-" .env 2>/dev/null; then \
			echo "  ✅ LLM_API_KEY 已配置"; \
		else \
			echo "  ⚠️  LLM_API_KEY 未配置"; \
		fi; \
	else \
		echo "  ❌ .env 文件不存在"; \
	fi
	@echo ""
	@echo "📚 详细状态: cat CURRENT_STATUS.md"
	@echo "📖 演示指南: cat DEMO_GUIDE.md"

# ============================================
# Docker 开发环境
# ============================================
setup:  ## 🐳 初始化 Docker 环境
	@echo "🚀 初始化 DeepResearch Docker 环境..."
	@echo ""
	@echo "📝 步骤 1/5: 创建环境变量文件"
	@if [ ! -f .env ]; then \
		cp .env.example .env 2>/dev/null || touch .env; \
		echo "✅ 已创建 .env 文件"; \
	else \
		echo "⚠️  .env 文件已存在，跳过"; \
	fi
	@echo ""
	@echo "📦 步骤 2/5: 安装后端依赖"
	@cd backend && poetry install || pip install -r requirements.txt
	@echo ""
	@echo "📦 步骤 3/5: 安装前端依赖"
	@cd frontend && npm install || pnpm install || echo "⚠️  前端依赖安装失败"
	@echo ""
	@echo "🐳 步骤 4/5: 启动数据库服务"
	@docker-compose up -d postgres redis || echo "⚠️  Docker 服务启动失败"
	@echo "⏳ 等待数据库就绪..."
	@sleep 5
	@echo ""
	@echo "✅ Docker 环境初始化完成！"
	@echo ""
	@echo "⚠️  重要提示："
	@echo "   1. 请编辑 .env 文件，填入你的 LLM API Key"
	@echo "   2. 运行 'make dev' 启动 Docker 环境"
	@echo "   3. 或运行 'make local-dev' 启动本地环境（推荐）"

# ============================================
# Docker 开发环境
# ============================================
dev:  ## 🐳 启动 Docker 环境（前台运行）
	@echo "🔧 启动 Docker 开发环境..."
	@docker-compose up

dev-bg:  ## 🐳 启动 Docker 环境（后台运行）
	@echo "🔧 启动 Docker 开发环境（后台）..."
	@docker-compose up -d
	@echo ""
	@echo "✅ 服务已启动！"
	@echo "   前端: http://localhost:3000"
	@echo "   后端: http://localhost:8000"
	@echo "   API 文档: http://localhost:8000/docs"
	@echo ""
	@echo "💡 查看日志: make logs"
	@echo "💡 停止服务: make stop"

stop:  ## 🛑 停止所有服务
	@echo "🛑 停止所有服务..."
	@docker-compose down

logs:  ## 📋 查看服务日志
	@docker-compose logs -f

logs-backend:  ## 📋 只查看后端日志
	@docker-compose logs -f backend

logs-frontend:  ## 📋 只查看前端日志
	@docker-compose logs -f frontend

# ============================================
# 测试
# ============================================
test:  ## 运行所有测试
	@echo "🧪 运行后端测试..."
	@cd backend && poetry run pytest -v
	@echo ""
	@echo "🧪 运行前端测试..."
	@cd frontend && pnpm test

test-backend:  ## 只运行后端测试
	@cd backend && poetry run pytest -v

test-frontend:  ## 只运行前端测试
	@cd frontend && pnpm test

test-cov:  ## 运行测试并生成覆盖率报告
	@cd backend && poetry run pytest --cov --cov-report=html
	@echo "📊 覆盖率报告: backend/htmlcov/index.html"

# ============================================
# 代码质量
# ============================================
lint:  ## 代码检查
	@echo "🔍 检查后端代码..."
	@cd backend && poetry run ruff check .
	@echo ""
	@echo "🔍 检查前端代码..."
	@cd frontend && pnpm lint

format:  ## 代码格式化
	@echo "✨ 格式化后端代码..."
	@cd backend && poetry run ruff format .
	@echo ""
	@echo "✨ 格式化前端代码..."
	@cd frontend && pnpm format

# ============================================
# 数据库
# ============================================
db-migrate:  ## 运行数据库迁移
	@cd backend && poetry run alembic upgrade head

db-rollback:  ## 回滚上一次迁移
	@cd backend && poetry run alembic downgrade -1

db-reset:  ## 重置数据库（危险操作！）
	@echo "⚠️  警告：这将删除所有数据！"
	@read -p "确认继续？(y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker-compose down -v postgres
	@docker-compose up -d postgres
	@echo "⏳ 等待数据库就绪..."
	@sleep 5
	@make db-migrate
	@echo "✅ 数据库已重置"

db-shell:  ## 进入数据库 Shell
	@docker-compose exec postgres psql -U postgres -d deep_research

# ============================================
# 清理
# ============================================
clean:  ## 清理缓存和临时文件
	@echo "🧹 清理缓存..."
	@docker-compose down -v
	@rm -rf backend/.cache backend/__pycache__ backend/**/__pycache__
	@rm -rf frontend/.next frontend/node_modules/.cache
	@echo "✅ 清理完成"

clean-all:  ## 深度清理（包括依赖）
	@echo "🧹 深度清理..."
	@make clean
	@rm -rf backend/.venv
	@rm -rf frontend/node_modules
	@echo "✅ 深度清理完成"

clean-docker:  ## 清理 Docker 缓存
	@./scripts/clean-docker.sh

rebuild:  ## 清理并重新构建
	@make clean-docker
	@make dev

# ============================================
# 部署
# ============================================
deploy:  ## 部署到生产环境
	@echo "🚀 部署到生产环境..."
	@./scripts/deploy.sh

build:  ## 构建生产镜像
	@echo "🏗️  构建生产镜像..."
	@docker-compose -f docker-compose.prod.yml build

# ============================================
# 开发工具
# ============================================
shell-backend:  ## 进入后端容器 Shell
	@docker-compose exec backend /bin/bash

shell-frontend:  ## 进入前端容器 Shell
	@docker-compose exec frontend /bin/sh

ps:  ## 查看运行中的服务
	@docker-compose ps

restart:  ## 重启所有服务
	@docker-compose restart

restart-backend:  ## 重启后端服务
	@docker-compose restart backend

restart-frontend:  ## 重启前端服务
	@docker-compose restart frontend

