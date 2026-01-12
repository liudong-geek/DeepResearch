# 🔧 故障排除指南

> 常见问题和解决方案

---

## 🐳 Docker 相关问题

### 问题 1: `ERR_PNPM_NO_LOCKFILE`

**错误信息**:
```
ERROR [frontend deps 2/2] RUN pnpm install --frozen-lockfile
ERR_PNPM_NO_LOCKFILE  Cannot install with "frozen-lockfile" because pnpm-lock.yaml is absent
```

**原因**: 前端项目缺少 `pnpm-lock.yaml` 文件

**解决方案**:

✅ **已修复**: Dockerfile 已更新，不再需要 lockfile

如果仍然遇到问题:
```bash
# 清理 Docker 缓存
./scripts/clean-docker.sh

# 重新构建
make dev
```

---

### 问题 2: Docker daemon 未运行

**错误信息**:
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**解决方案**:
```bash
# macOS: 启动 Docker Desktop
open /Applications/Docker.app

# 等待 Docker 图标变为绿色（约 30 秒）

# 验证 Docker 已启动
docker ps
```

---

### 问题 3: 端口被占用

**错误信息**:
```
Error: port is already allocated
```

**解决方案**:
```bash
# 查看占用端口的进程
lsof -i :8000  # 后端
lsof -i :3000  # 前端
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# 杀死进程
kill -9 <PID>

# 或者修改端口（编辑 .env 文件）
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

---

### 问题 4: Docker 构建缓存问题

**症状**: 修改代码后，Docker 容器没有更新

**解决方案**:
```bash
# 方式 1: 清理并重建
make clean-docker
make dev

# 方式 2: 强制重建
docker-compose build --no-cache
docker-compose up -d

# 方式 3: 删除所有容器和镜像
docker-compose down -v
docker system prune -a
make dev
```

---

## 🐍 Python/后端问题

### 问题 5: Poetry 未安装

**错误信息**:
```
zsh:1: command not found: poetry
```

**解决方案**:

**方式 A: 安装 Poetry**
```bash
./scripts/install-poetry.sh
source ~/.zshrc
```

**方式 B: 使用 pip（推荐）**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**方式 C: 使用启动脚本**
```bash
./scripts/start-backend.sh
```

---

### 问题 6: 数据库连接失败

**错误信息**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案**:
```bash
# 1. 检查数据库是否运行
docker-compose ps postgres

# 2. 查看数据库日志
docker-compose logs postgres

# 3. 重启数据库
docker-compose restart postgres

# 4. 检查环境变量
cat .env | grep DATABASE_URL

# 5. 确保 DATABASE_URL 正确
# 本地开发应该是:
DATABASE_URL=postgresql+asyncpg://deepresearch:deepresearch123@localhost:5432/deepresearch
```

---

### 问题 7: 依赖安装失败

**错误信息**:
```
ERROR: Could not find a version that satisfies the requirement ...
```

**解决方案**:
```bash
# 1. 升级 pip
pip install --upgrade pip

# 2. 清理缓存
pip cache purge

# 3. 重新安装
pip install -r requirements.txt

# 4. 如果使用 Poetry
poetry cache clear pypi --all
poetry install
```

---

## 🎨 前端问题

### 问题 8: pnpm 未安装

**错误信息**:
```
zsh:1: command not found: pnpm
```

**解决方案**:
```bash
# 安装 pnpm
npm install -g pnpm

# 验证安装
pnpm --version
```

---

### 问题 9: 前端依赖安装失败

**错误信息**:
```
ERR_PNPM_...
```

**解决方案**:
```bash
cd frontend

# 1. 清理缓存
pnpm store prune

# 2. 删除 node_modules
rm -rf node_modules pnpm-lock.yaml

# 3. 重新安装
pnpm install

# 4. 如果还是失败，使用 npm
npm install
```

---

### 问题 10: 前端无法连接后端

**错误信息**:
```
Failed to fetch
Network Error
```

**解决方案**:
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/api/health

# 2. 检查 CORS 配置
# 编辑 backend/api/main.py，确保 CORS 允许前端域名

# 3. 检查环境变量
# 编辑 frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🗄️ 数据库问题

### 问题 11: 数据库迁移失败

**错误信息**:
```
alembic.util.exc.CommandError: ...
```

**解决方案**:
```bash
cd backend

# 1. 检查迁移历史
poetry run alembic history

# 2. 查看当前版本
poetry run alembic current

# 3. 重置数据库（⚠️ 会删除所有数据）
docker-compose down -v
docker-compose up -d postgres redis
sleep 5

# 4. 运行迁移
poetry run alembic upgrade head
```

---

### 问题 12: PostgreSQL 容器启动失败

**错误信息**:
```
Error: Database is uninitialized and superuser password is not specified
```

**解决方案**:
```bash
# 1. 检查 .env 文件
cat .env | grep POSTGRES

# 2. 确保环境变量正确
POSTGRES_USER=deepresearch
POSTGRES_PASSWORD=deepresearch123
POSTGRES_DB=deepresearch

# 3. 删除数据卷并重启
docker-compose down -v
docker-compose up -d postgres
```

---

## 🚀 性能问题

### 问题 13: Docker 容器启动慢

**症状**: `docker-compose up` 需要很长时间

**解决方案**:
```bash
# 1. 增加 Docker 资源
# Docker Desktop -> Settings -> Resources
# - CPUs: 4+
# - Memory: 8GB+

# 2. 使用本地开发模式
./scripts/start-backend.sh  # 终端 1
./scripts/start-frontend.sh # 终端 2

# 3. 只启动数据库
docker-compose -f docker-compose.dev.yml up -d
```

---

## 📝 其他问题

### 问题 14: 找不到模块

**错误信息**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:
```bash
# 1. 确保在虚拟环境中
source backend/.venv/bin/activate

# 2. 重新安装依赖
pip install -r backend/requirements.txt

# 3. 检查 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

---

### 问题 15: 权限问题

**错误信息**:
```
Permission denied
```

**解决方案**:
```bash
# 给脚本添加执行权限
chmod +x scripts/*.sh

# 修复文件所有权
sudo chown -R $USER:$USER .
```

---

## 🆘 获取帮助

如果以上方案都无法解决你的问题:

1. **查看日志**:
   ```bash
   # Docker 日志
   docker-compose logs -f
   
   # 后端日志
   tail -f backend/logs/app.log
   ```

2. **检查系统要求**:
   - Docker Desktop 已启动
   - Python 3.11+
   - Node.js 20+
   - 足够的磁盘空间（至少 5GB）

3. **重置项目**:
   ```bash
   make clean-all
   make setup
   make dev
   ```

4. **联系支持**:
   - 提交 Issue
   - 附上错误日志
   - 说明操作系统和版本

---

**祝你好运！** 🍀

