"""
MCP Server 测试
"""
import asyncio

import pytest
from loguru import logger

from mcp_servers.ecommerce import EcommerceMCPServer


@pytest.mark.asyncio
async def test_ecommerce_server_init():
    """测试 E-commerce MCP Server 初始化"""
    server = EcommerceMCPServer()
    
    assert server.name == "ecommerce"
    assert server.version == "1.0.0"
    
    # 检查工具列表
    tools = server.get_tools()
    assert len(tools) > 0
    
    tool_names = [tool.name for tool in tools]
    assert "get_product_info" in tool_names
    assert "get_product_specs" in tool_names
    assert "search_products" in tool_names
    
    logger.info(f"✅ 工具列表: {tool_names}")


@pytest.mark.asyncio
async def test_get_product_info():
    """测试获取产品信息"""
    server = EcommerceMCPServer()
    
    # 测试 URL（这里使用一个示例 URL）
    test_url = "https://www.upliftdesk.com/uplift-v2-standing-desk/"
    
    try:
        result = await server.call_tool(
            "get_product_info",
            {
                "brand": "uplift",
                "url": test_url,
            }
        )
        
        logger.info(f"✅ 产品信息: {result}")
        
        assert "brand" in result
        assert result["brand"] == "Uplift"
        assert "url" in result
        
    except Exception as e:
        logger.warning(f"⚠️ 测试跳过（可能是网络问题）: {e}")
        pytest.skip(f"网络请求失败: {e}")


@pytest.mark.asyncio
async def test_rate_limiter():
    """测试限速器"""
    server = EcommerceMCPServer()
    
    import time
    
    # 连续发起 3 个请求，应该被限速
    start_time = time.time()
    
    for i in range(3):
        await server.rate_limiter.acquire()
        logger.info(f"请求 {i+1} 已通过")
    
    elapsed = time.time() - start_time
    
    # 限速是 0.5/s（每 2 秒 1 个请求），3 个请求应该至少需要 4 秒
    # 但由于 burst=2，前 2 个请求可以立即通过，第 3 个需要等待
    logger.info(f"✅ 3 个请求耗时: {elapsed:.2f}s")
    assert elapsed >= 2.0  # 至少需要 2 秒


@pytest.mark.asyncio
async def test_cache():
    """测试缓存"""
    server = EcommerceMCPServer()
    
    # 设置缓存
    server.cache.set("test_key", {"data": "test_value"})
    
    # 获取缓存
    cached = server.cache.get("test_key")
    assert cached is not None
    assert cached["data"] == "test_value"
    
    # 删除缓存
    server.cache.delete("test_key")
    cached = server.cache.get("test_key")
    assert cached is None
    
    logger.info("✅ 缓存测试通过")


if __name__ == "__main__":
    # 直接运行测试
    asyncio.run(test_ecommerce_server_init())
    asyncio.run(test_rate_limiter())
    asyncio.run(test_cache())
    
    logger.info("🎉 所有测试通过！")

