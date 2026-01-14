"""
调研任务路由
"""
from typing import List, Dict, Any
from uuid import UUID, uuid4
import asyncio
import os

from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger
from pydantic import BaseModel, Field

from orchestrator import ResearchOrchestrator

router = APIRouter()

# 全局任务存储（生产环境应该使用数据库）
research_tasks: Dict[UUID, Dict[str, Any]] = {}


# ============================================
# 请求/响应模型
# ============================================

class ResearchRequest(BaseModel):
    """调研请求"""
    keyword: str = Field(default="standing desk", description="产品关键词")
    market: str = Field(default="US", description="目标市场")
    competitors: List[str] = Field(
        ...,
        min_items=1,
        description="竞品列表，至少1个",
        example=["Uplift", "Jarvis", "Vari"]
    )


class ResearchResponse(BaseModel):
    """调研响应"""
    task_id: UUID
    status: str
    message: str


class ResearchStatus(BaseModel):
    """调研状态"""
    task_id: UUID
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    current_step: str
    error: str | None = None


class ResearchResult(BaseModel):
    """调研结果"""
    task_id: UUID
    keyword: str
    market: str
    competitors: List[str]

    # 元数据
    metadata: dict | None = None

    # 竞品对比表
    comparison_table: dict

    # 评论洞察
    review_insights: dict

    # Reddit 讨论
    reddit_discussions: list | None = None

    # 行动计划
    action_plan: dict

    # 效率对比
    efficiency_comparison: dict


# ============================================
# 后台任务
# ============================================

# 竞品 URL 映射
COMPETITOR_URLS = {
    # Premium 品牌
    "uplift": "https://www.upliftdesk.com/uplift-v2-standing-desk-v2-or-v2-commercial/",
    "vari": "https://www.vari.com/electric-standing-desk-60x30/FD-ESD6030.html",
    "jarvis": "https://www.fully.com/standing-desks/jarvis.html",
    "humanscale": "https://www.humanscale.com/products/standing-desks/quickstand-eco-desk-converter",  # 更新为有价格的产品

    # Mid-range 品牌
    "flexispot": "https://www.flexispot.com/height-adjustable-desks/electric-height-adjustable-standing-desk-e7",
    "autonomous": "https://www.autonomous.ai/standing-desks/smartdesk-2-home",

    # Budget 品牌
    "ikea": "https://www.ikea.com/us/en/p/bekant-desk-sit-stand-white-s49022538/",
    "monoprice": "https://www.monoprice.com/product?p_id=15722",
}


async def run_research_task(task_id: UUID, request: ResearchRequest):
    """
    运行调研任务（后台）
    """
    try:
        # 更新状态
        research_tasks[task_id]["status"] = "running"
        research_tasks[task_id]["progress"] = 10
        research_tasks[task_id]["current_step"] = "初始化 Orchestrator..."

        # 创建 Orchestrator（会自动从环境变量读取 LLM 配置）
        orchestrator = ResearchOrchestrator()

        # 构建竞品列表
        competitors = []
        for comp_name in request.competitors:
            comp_lower = comp_name.lower()
            url = COMPETITOR_URLS.get(comp_lower)
            if url:
                competitors.append({
                    "brand": comp_lower,
                    "url": url
                })
            else:
                logger.warning(f"未找到竞品 URL: {comp_name}")

        if not competitors:
            raise ValueError("没有有效的竞品")

        # 定义进度回调函数
        def update_progress(step: int, total_steps: int, message: str):
            """更新任务进度"""
            # 计算进度百分比（20% - 95%，留 5% 给最后的清理工作）
            progress = 20 + int((step / total_steps) * 75)
            research_tasks[task_id]["progress"] = progress
            research_tasks[task_id]["current_step"] = message
            logger.info(f"[Task {task_id}] {progress}% - {message}")

        # 更新进度
        update_progress(0, 6, f"开始调研 {len(competitors)} 个竞品...")

        # 运行调研（传入进度回调）
        logger.info(f"[Task {task_id}] 开始调研...")
        result = await orchestrator.run_research(
            keyword=request.keyword,
            market=request.market,
            competitors=competitors,
            progress_callback=update_progress
        )

        # 清理资源
        research_tasks[task_id]["progress"] = 95
        research_tasks[task_id]["current_step"] = "清理资源..."
        await orchestrator.cleanup()

        # 更新任务状态
        research_tasks[task_id]["status"] = "completed"
        research_tasks[task_id]["progress"] = 100
        research_tasks[task_id]["current_step"] = "调研完成"
        research_tasks[task_id]["result"] = result

        logger.info(f"[Task {task_id}] 调研完成")

    except Exception as e:
        logger.error(f"[Task {task_id}] 调研失败: {e}")
        research_tasks[task_id]["status"] = "failed"
        research_tasks[task_id]["error"] = str(e)
        research_tasks[task_id]["current_step"] = f"失败: {str(e)}"



# ============================================
# 路由处理器
# ============================================

@router.post("/start", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    启动调研任务

    创建一个新的调研任务并返回任务 ID
    """
    logger.info(f"收到调研请求: keyword={request.keyword}, competitors={request.competitors}")

    # 创建任务 ID
    task_id = uuid4()

    # 初始化任务状态
    research_tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "current_step": "初始化...",
        "keyword": request.keyword,
        "market": request.market,
        "competitors": request.competitors,
        "result": None,
        "error": None,
    }

    # 启动后台任务
    background_tasks.add_task(run_research_task, task_id, request)

    logger.info(f"调研任务已创建: task_id={task_id}")

    return ResearchResponse(
        task_id=task_id,
        status="pending",
        message=f"调研任务已创建，任务 ID: {task_id}"
    )


@router.get("/{task_id}/status", response_model=ResearchStatus)
async def get_research_status(task_id: UUID):
    """
    获取调研任务状态

    返回任务的当前状态和进度
    """
    logger.info(f"查询任务状态: task_id={task_id}")

    # 从内存查询任务状态
    task = research_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return ResearchStatus(
        task_id=task["task_id"],
        status=task["status"],
        progress=task["progress"],
        current_step=task["current_step"],
        error=task.get("error")
    )


@router.get("/{task_id}/result", response_model=ResearchResult)
async def get_research_result(task_id: UUID):
    """
    获取调研结果

    返回完整的调研报告
    """
    logger.info(f"获取调研结果: task_id={task_id}")

    # 从内存查询任务
    task = research_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 检查任务状态
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"任务尚未完成，当前状态: {task['status']}"
        )

    # 返回结果
    result = task["result"]
    return ResearchResult(
        task_id=task["task_id"],
        keyword=task["keyword"],
        market=task["market"],
        competitors=task["competitors"],
        metadata=result.get("metadata"),
        comparison_table=result.get("comparison_table", {}),
        review_insights=result.get("review_insights", {}),
        reddit_discussions=result.get("reddit_discussions"),
        action_plan=result.get("action_plan", {}),
        efficiency_comparison=result.get("efficiency_comparison", {}),
    )


@router.get("/", response_model=List[ResearchStatus])
async def list_research_tasks(limit: int = 10, offset: int = 0):
    """
    列出所有调研任务

    返回任务列表（分页）
    """
    logger.info(f"列出调研任务: limit={limit}, offset={offset}")

    # TODO: 从数据库查询任务列表

    # 临时实现
    return []


@router.delete("/{task_id}")
async def delete_research_task(task_id: UUID):
    """
    删除调研任务

    删除指定的调研任务及其结果
    """
    logger.info(f"删除调研任务: task_id={task_id}")

    # TODO: 从数据库删除任务

    return {"message": f"任务 {task_id} 已删除"}

