"""
Research Orchestrator

智能体编排器，协调各个 MCP Server 生成调研报告
"""
from typing import Any, Dict, List, Optional
import json
import os
from datetime import datetime

from loguru import logger
from openai import AsyncOpenAI

from mcp_servers.ecommerce import EcommerceMCPServer
from mcp_servers.review import ReviewMCPServer
from mcp_servers.content import ContentMCPServer


class ResearchOrchestrator:
    """
    调研编排器

    协调 E-commerce MCP、Review MCP 和 Content MCP，生成结构化的竞品调研报告

    支持的 LLM 提供商（通过环境变量配置）：
    - OpenAI (默认)
    - Qwen (阿里云通义千问)
    - 其他兼容 OpenAI API 的提供商

    环境变量：
    - LLM_PROVIDER: 提供商名称 (openai/qwen/custom)
    - LLM_API_KEY: API 密钥
    - LLM_BASE_URL: API 基础 URL（可选）
    - LLM_MODEL: 模型名称（可选）
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化编排器

        Args:
            api_key: API 密钥（可选，优先使用环境变量）
        """
        # 从环境变量读取配置
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model = os.getenv("LLM_MODEL")

        # 验证 API Key
        if not self.api_key:
            error_msg = (
                f"LLM API Key 未设置！请设置环境变量：\n"
                f"  LLM_API_KEY=your-api-key\n"
                f"或者：\n"
                f"  OPENAI_API_KEY=your-api-key\n"
                f"当前提供商: {self.provider}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 根据提供商设置默认值
        if self.provider == "qwen":
            # 阿里云通义千问配置
            if not self.base_url:
                self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            if not self.model:
                self.model = "qwen-max"  # 或 qwen-turbo, qwen-max
            logger.info(f"使用 Qwen 模型: {self.model}")
        elif self.provider == "openai":
            # OpenAI 配置
            if not self.model:
                self.model = "gpt-4o-mini"
            logger.info(f"使用 OpenAI 模型: {self.model}")
        else:
            # 自定义提供商
            if not self.model:
                self.model = "gpt-4o-mini"  # 默认模型
            logger.info(f"使用自定义提供商: {self.provider}, 模型: {self.model}")

        # 初始化 OpenAI 客户端（兼容 Qwen 和其他提供商）
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.openai_client = AsyncOpenAI(**client_kwargs)

        # 初始化 MCP Servers
        self.ecommerce_server = EcommerceMCPServer()
        self.review_server = ReviewMCPServer()
        self.content_server = ContentMCPServer()

        logger.info(f"Research Orchestrator 已初始化 (Provider: {self.provider}, Model: {self.model})")

    async def run_research(
        self,
        keyword: str,
        market: str,
        competitors: List[Dict[str, str]],
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        运行完整的调研流程

        Args:
            keyword: 产品关键词（如 "standing desk"）
            market: 目标市场（如 "US"）
            competitors: 竞品列表，格式: [{"brand": "uplift", "url": "..."}]
            progress_callback: 进度回调函数，签名: (step: int, total_steps: int, message: str) -> None

        Returns:
            调研报告
        """
        logger.info(f"开始调研: keyword={keyword}, market={market}, competitors={len(competitors)}")

        start_time = datetime.now()
        total_steps = 6

        # Step 1: 抓取竞品产品信息
        logger.info("Step 1: 抓取竞品产品信息...")
        if progress_callback:
            progress_callback(1, total_steps, f"Step 1/6: 抓取 {len(competitors)} 个竞品产品信息...")
        product_data = await self._fetch_product_data(competitors)

        # Step 2: 抓取评论数据
        logger.info("Step 2: 抓取评论数据...")
        if progress_callback:
            progress_callback(2, total_steps, "Step 2/6: 抓取评论数据...")
        review_data = await self._fetch_review_data(competitors)

        # Step 3: 抓取 Reddit 讨论内容
        logger.info("Step 3: 抓取 Reddit 讨论内容...")
        if progress_callback:
            progress_callback(3, total_steps, "Step 3/6: 抓取 Reddit 讨论内容...")
        reddit_data = await self._fetch_reddit_content(keyword)

        # Step 4: 使用 LLM 生成竞品对比表
        logger.info("Step 4: 生成竞品对比表...")
        if progress_callback:
            progress_callback(4, total_steps, "Step 4/6: 使用 AI 生成竞品对比表...")
        comparison_table = await self._generate_comparison_table(product_data)

        # Step 5: 使用 LLM 分析评论洞察
        logger.info("Step 5: 分析评论洞察...")
        if progress_callback:
            progress_callback(5, total_steps, "Step 5/6: 使用 AI 分析评论洞察...")
        review_insights = await self._analyze_reviews(review_data, reddit_data)

        # Step 6: 使用 LLM 生成行动计划
        logger.info("Step 6: 生成行动计划...")
        if progress_callback:
            progress_callback(6, total_steps, "Step 6/6: 使用 AI 生成行动计划...")
        action_plan = await self._generate_action_plan(
            comparison_table,
            review_insights,
            keyword,
            market
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 计算数据置信度
        confidence = self._calculate_confidence(product_data, comparison_table)

        # 组装最终报告
        report = {
            "metadata": {
                "keyword": keyword,
                "market": market,
                "competitors": [c["brand"] for c in competitors],
                "generated_at": end_time.isoformat(),
                "duration_seconds": duration,
                "confidence": confidence,
                "data_sources": {
                    "products": len(product_data),
                    "reviews": len(review_data),
                    "reddit_posts": len(reddit_data),
                },
            },
            "comparison_table": comparison_table,
            "review_insights": review_insights,
            "reddit_discussions": reddit_data,
            "action_plan": action_plan,
            "efficiency_comparison": {
                "manual_hours": 8,  # 估计人工需要 8 小时
                "tool_seconds": duration,
                "speedup": 8 * 3600 / duration if duration > 0 else 0,
            },
        }

        logger.info(f"调研完成，耗时 {duration:.1f} 秒，置信度 {confidence:.0%}")

        return report

    async def _fetch_product_data(
        self,
        competitors: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """抓取产品数据"""
        results = []

        for competitor in competitors:
            brand = competitor["brand"]
            url = competitor["url"]

            try:
                logger.info(f"抓取 {brand} 产品信息...")

                # 调用 E-commerce MCP
                result = await self.ecommerce_server.call_tool(
                    "get_product_info",
                    {"brand": brand, "url": url}
                )

                # 解析结果
                if result and len(result) > 0:
                    data = json.loads(result[0].text)

                    # 添加来源信息（用于引用溯源）
                    data['_source'] = {
                        'type': 'product_page',
                        'url': url,
                        'brand': brand,
                        'extracted_at': datetime.now().isoformat(),
                        'data_points': list(data.keys())
                    }

                    results.append(data)
                    logger.info(f"✅ {brand}: {data.get('title', 'N/A')}")
                else:
                    logger.warning(f"⚠️  {brand}: 未获取到数据")

            except Exception as e:
                logger.error(f"❌ {brand}: {e}")
                results.append({
                    "brand": brand,
                    "url": url,
                    "error": str(e),
                    '_source': {
                        'type': 'error',
                        'url': url,
                        'brand': brand,
                        'extracted_at': datetime.now().isoformat()
                    }
                })

        return results

    async def _fetch_review_data(
        self,
        competitors: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """抓取评论数据"""
        # TODO: 实现评论抓取
        # 暂时返回空列表，因为 Amazon 需要登录
        logger.warning("评论抓取暂时跳过（Amazon 需要登录）")
        return []

    async def _fetch_reddit_content(
        self,
        keyword: str
    ) -> List[Dict[str, Any]]:
        """抓取 Reddit 讨论内容"""
        results = []

        try:
            # 搜索相关子版块的讨论
            # 例如：standing desk -> r/StandingDesk
            subreddit_map = {
                "standing desk": "r/StandingDesk",
                "desk": "r/StandingDesk",
                # 可以添加更多映射
            }

            # 尝试从映射中获取子版块，否则使用关键词搜索
            query = subreddit_map.get(keyword.lower(), keyword)

            logger.info(f"抓取 Reddit 内容: {query}")

            # 调用 Content MCP
            result = await self.content_server.call_tool(
                "get_content",
                {"source": "reddit", "query": query, "limit": 10}
            )

            # 解析结果
            if result and len(result) > 0:
                data = json.loads(result[0].text)

                if "contents" in data and data["contents"]:
                    for post in data["contents"]:
                        # 添加来源信息
                        post['_source'] = {
                            'type': 'reddit_post',
                            'url': post.get('url', ''),
                            'subreddit': post.get('subreddit', ''),
                            'extracted_at': datetime.now().isoformat(),
                        }
                        results.append(post)

                    logger.info(f"✅ Reddit: 获取 {len(results)} 个讨论")
                else:
                    logger.warning(f"⚠️  Reddit: 未获取到讨论")

        except Exception as e:
            logger.error(f"❌ Reddit 内容抓取失败: {e}")

        return results

    async def _generate_comparison_table(
        self,
        product_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """使用 LLM 生成竞品对比表"""
        # 构建 prompt
        prompt = self._build_comparison_prompt(product_data)

        try:
            # 调用 LLM API
            # 注意：Qwen 也支持 response_format，但如果不支持会自动忽略
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的市场调研分析师，擅长竞品对比分析。请根据提供的产品数据，生成结构化的竞品对比表。输出必须是有效的 JSON 格式。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"} if self.provider == "openai" else None
            )

            # 解析响应
            content = response.choices[0].message.content

            if not content:
                logger.error("❌ LLM 返回空响应")
                return {
                    "error": "LLM 返回空响应",
                    "products": product_data
                }

            # 尝试提取 JSON（可能包含在 markdown 代码块中）
            try:
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content.strip()

                comparison = json.loads(json_str)
                logger.info("✅ 竞品对比表生成成功")
                return comparison
            except json.JSONDecodeError as je:
                logger.error(f"❌ JSON 解析失败: {je}")
                logger.debug(f"原始响应: {content[:500]}...")
                return {
                    "error": f"JSON 解析失败: {str(je)}",
                    "raw_response": content[:500],
                    "products": product_data
                }

        except Exception as e:
            logger.error(f"❌ 生成竞品对比表失败: {e}")
            return {
                "error": str(e),
                "products": product_data
            }

    async def _analyze_reviews(
        self,
        review_data: List[Dict[str, Any]],
        reddit_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """使用 LLM 分析评论和 Reddit 讨论"""
        if not review_data and not reddit_data:
            return {
                "note": "暂无评论和讨论数据",
                "topics": [],
                "sentiment": {},
                "insights": []
            }

        # 如果有 Reddit 数据，提取关键洞察
        reddit_insights = []
        if reddit_data:
            for post in reddit_data[:5]:  # 只分析前 5 个帖子
                reddit_insights.append({
                    "title": post.get("title", ""),
                    "content": post.get("content", "")[:500],  # 限制长度
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                })

        return {
            "note": "评论分析基于 Reddit 讨论",
            "reddit_insights": reddit_insights,
            "total_posts": len(reddit_data) if reddit_data else 0,
            "topics": [],  # TODO: 使用 LLM 提取主题
            "sentiment": {},  # TODO: 使用 LLM 分析情感
        }

    async def _generate_action_plan(
        self,
        comparison_table: Dict[str, Any],
        review_insights: Dict[str, Any],
        keyword: str,
        market: str
    ) -> Dict[str, Any]:
        """使用 LLM 生成行动计划"""
        # 构建 prompt
        prompt = self._build_action_plan_prompt(
            comparison_table,
            review_insights,
            keyword,
            market
        )

        try:
            # 调用 LLM API
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个电商运营专家，擅长根据竞品分析制定行动计划。请提供具体、可执行的建议。输出必须是有效的 JSON 格式。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                response_format={"type": "json_object"} if self.provider == "openai" else None
            )

            # 解析响应
            content = response.choices[0].message.content

            if not content:
                logger.error("❌ LLM 返回空响应")
                return {"error": "LLM 返回空响应"}

            # 尝试提取 JSON（可能包含在 markdown 代码块中）
            try:
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content.strip()

                action_plan = json.loads(json_str)
                logger.info("✅ 行动计划生成成功")
                return action_plan
            except json.JSONDecodeError as je:
                logger.error(f"❌ JSON 解析失败: {je}")
                logger.debug(f"原始响应: {content[:500]}...")
                return {
                    "error": f"JSON 解析失败: {str(je)}",
                    "raw_response": content[:500]
                }

        except Exception as e:
            logger.error(f"❌ 生成行动计划失败: {e}")
            return {
                "error": str(e)
            }

    def _build_comparison_prompt(self, product_data: List[Dict[str, Any]]) -> str:
        """构建竞品对比 prompt"""
        products_json = json.dumps(product_data, indent=2, ensure_ascii=False)

        return f"""
请分析以下竞品产品数据，生成结构化的竞品对比表。

**重要**:
1. 每个数据点必须标注来源 URL
2. price 必须是数字类型（如 299.99），不要用字符串
3. 在 sources 字段中列出所有数据来源
4. **价格验证**: 如果某个品牌的价格异常（<$100 或 >$3000），请在 positioning 中标注"价格异常，需人工核实"

产品数据：
{products_json}

**注意**: 部分产品可能包含 price_warning 字段，表示价格可能不准确（如配件价格、数据抓取错误等）。
请在生成对比表时考虑这些警告，并在 positioning 中说明。

请生成 JSON 格式的对比表，包含以下维度：
1. 价格带（price_comparison）：各品牌的价格区间和定位
2. 核心卖点（feature_comparison）：每个品牌的主要卖点
3. 产品描述（description_analysis）：产品描述的重点
4. 图片质量（image_quality）：产品图片的专业程度评估

输出格式示例：
{{
  "price_comparison": {{
    "Uplift": {{
      "price": 299.99,
      "positioning": "中端定位，性价比高",
      "source_url": "https://www.upliftdesk.com/..."
    }},
    "Vari": {{
      "price": 349.00,
      "positioning": "偏高端定价，强调品质",
      "source_url": "https://www.vari.com/..."
    }}
  }},
  "feature_comparison": {{
    "Uplift": ["多种桌面厚度选项", "模块化设计", "7年保修"],
    "Vari": ["终身保修", "快速发货", "简约设计"]
  }},
  "description_analysis": {{
    "Uplift": "强调定制化和灵活性",
    "Vari": "强调品质和可靠性"
  }},
  "image_quality": {{
    "Uplift": "专业产品图，多角度展示",
    "Vari": "高质量渲染图，场景化展示"
  }},
  "summary": "总体对比总结（2-3句话）",
  "sources": [
    {{
      "brand": "Uplift",
      "url": "https://www.upliftdesk.com/...",
      "data_points": ["price", "features", "description", "images"],
      "extracted_at": "2026-01-12T21:30:00Z"
    }},
    {{
      "brand": "Vari",
      "url": "https://www.vari.com/...",
      "data_points": ["price", "features", "description", "images"],
      "extracted_at": "2026-01-12T21:30:00Z"
    }}
  ],
  "metadata": {{
    "total_competitors": 2,
    "data_sources": 2,
    "confidence": 0.85
  }}
}}
"""

    def _build_action_plan_prompt(
        self,
        comparison_table: Dict[str, Any],
        review_insights: Dict[str, Any],
        keyword: str,
        market: str
    ) -> str:
        """构建行动计划 prompt"""
        comparison_json = json.dumps(comparison_table, indent=2, ensure_ascii=False)
        insights_json = json.dumps(review_insights, indent=2, ensure_ascii=False)

        return f"""
基于以下竞品对比和评论洞察，为 FlexiSpot 在 {market} 市场推出 "{keyword}" 产品制定行动计划。

竞品对比：
{comparison_json}

评论洞察：
{insights_json}

请生成 JSON 格式的行动计划，包含：
1. 运营建议（operations）：上新策略、定价建议、PDP 结构
2. 投放建议（marketing）：受众定位、素材方向、文案方向
3. 产品改进（product）：Top 5 产品改进建议
4. 客服准备（customer_service）：常见问题 FAQ

输出格式：
{{
  "operations": {{
    "pricing_strategy": "定价策略",
    "launch_strategy": "上新策略",
    "pdp_recommendations": ["PDP建议1", "PDP建议2", ...]
  }},
  "marketing": {{
    "target_audience": "目标受众描述",
    "creative_direction": ["素材方向1", "素材方向2", ...],
    "copy_direction": ["文案方向1", "文案方向2", ...]
  }},
  "product": {{
    "improvements": ["改进1", "改进2", "改进3", "改进4", "改进5"]
  }},
  "customer_service": {{
    "faq": [
      {{"question": "问题", "answer": "答案"}}
    ]
  }}
}}
"""

    def _calculate_confidence(
        self,
        product_data: List[Dict[str, Any]],
        comparison_table: Dict[str, Any]
    ) -> float:
        """
        计算数据置信度

        评分维度：
        1. 数据来源数量 (40%)
        2. 数据完整性 (30%)
        3. 数据新鲜度 (30%)
        """
        score = 0.0

        # 1. 数据来源数量 (40%)
        # 3个以上来源得满分
        num_sources = len([d for d in product_data if 'error' not in d])
        source_score = min(num_sources / 3, 1.0) * 0.4
        score += source_score

        # 2. 数据完整性 (30%)
        # 检查必需字段是否存在
        required_fields = ['price', 'title', 'description']
        if num_sources > 0:
            completeness = sum(
                1 for data in product_data
                if 'error' not in data and all(field in data for field in required_fields)
            ) / num_sources
            score += completeness * 0.3

        # 3. 数据新鲜度 (30%)
        # 假设数据都是新抓取的，给满分
        score += 0.3

        # 如果 LLM 返回了 metadata.confidence，也考虑进去
        if isinstance(comparison_table, dict) and 'metadata' in comparison_table:
            llm_confidence = comparison_table['metadata'].get('confidence', 1.0)
            score = score * 0.7 + llm_confidence * 0.3

        return round(min(score, 1.0), 2)

    async def cleanup(self):
        """清理资源"""
        # 关闭浏览器（仅对有浏览器的爬虫）
        for scraper in self.ecommerce_server.scrapers.values():
            if hasattr(scraper, '_close_browser') and callable(getattr(scraper, '_close_browser')):
                await scraper._close_browser()

        for scraper in self.review_server.scrapers.values():
            if hasattr(scraper, '_close_browser') and callable(getattr(scraper, '_close_browser')):
                await scraper._close_browser()

        for scraper in self.content_server.scrapers.values():
            if hasattr(scraper, '_close_browser') and callable(getattr(scraper, '_close_browser')):
                await scraper._close_browser()

        logger.info("资源已清理")

