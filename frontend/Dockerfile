# ============================================
# DeepResearch Frontend Dockerfile
# ============================================

FROM node:20-alpine AS base

# 安装 pnpm
RUN npm install -g pnpm

# 设置工作目录
WORKDIR /app

# ============================================
# 依赖安装阶段
# ============================================
FROM base AS deps

# 复制依赖文件
COPY package.json pnpm-lock.yaml* ./

# 安装依赖（如果没有 lockfile 则生成）
RUN pnpm install

# ============================================
# 开发环境
# ============================================
FROM base AS development

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["pnpm", "dev"]

# ============================================
# 构建阶段
# ============================================
FROM base AS builder

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules

# 复制源代码
COPY . .

# 构建应用
RUN pnpm build

# ============================================
# 生产环境
# ============================================
FROM base AS production

# 设置环境变量
ENV NODE_ENV=production

# 复制构建产物
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# 暴露端口
EXPOSE 3000

# 启动生产服务器
CMD ["node", "server.js"]

