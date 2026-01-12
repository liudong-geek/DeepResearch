"""
DeepResearch FastAPI 应用入口
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.routes import health, research
from db.database import init_db, close_db
from mcp_servers.ecommerce import EcommerceMCPServer


# ============================================
# 加载环境变量
# ============================================
# 查找项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"✅ 已加载环境变量: {env_path}")
else:
    logger.warning(f"⚠️  未找到 .env 文件: {env_path}")


# 全局 MCP Server 实例
ecommerce_server: EcommerceMCPServer | None = None


# ============================================
# 应用生命周期管理
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    global ecommerce_server

    # 启动时执行
    logger.info("🚀 DeepResearch 后端服务启动中...")
    logger.info(f"环境: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"日志级别: {os.getenv('LOG_LEVEL', 'INFO')}")

    # 初始化数据库
    try:
        await init_db()
        logger.info("✅ 数据库初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")

    # 初始化 MCP Servers
    try:
        ecommerce_server = EcommerceMCPServer()
        logger.info("✅ E-commerce MCP Server 初始化成功")
    except Exception as e:
        logger.error(f"❌ MCP Server 初始化失败: {e}")

    logger.info("🎉 DeepResearch 后端服务启动完成")

    yield

    # 关闭时执行
    logger.info("🛑 DeepResearch 后端服务关闭中...")
    await close_db()
    logger.info("👋 DeepResearch 后端服务已关闭")


# ============================================
# 创建 FastAPI 应用
# ============================================
app = FastAPI(
    title="DeepResearch API",
    description="竞品调研智能体后端 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================
# CORS 中间件
# ============================================
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# 注册路由
# ============================================
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(research.router, prefix="/api/research", tags=["调研"])


# ============================================
# 根路径
# ============================================
@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "name": "DeepResearch API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


# ============================================
# 日志配置
# ============================================
def configure_logging():
    """配置日志"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "text")
    
    # 移除默认 handler
    logger.remove()
    
    # 添加新的 handler
    if log_format == "json":
        logger.add(
            "logs/app.log",
            format="{time} {level} {message}",
            level=log_level,
            rotation="1 day",
            retention="7 days",
            serialize=True,
        )
    else:
        logger.add(
            "logs/app.log",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            rotation="1 day",
            retention="7 days",
        )
    
    # 同时输出到控制台
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True,
    )


# 配置日志
configure_logging()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

