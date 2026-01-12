#!/usr/bin/env python3
"""
端到端测试 - 完整流程
"""
import asyncio
import sys
import os
import json

# 添加 backend 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_end_to_end():
    """端到端测试"""
    from orchestrator import ResearchOrchestrator
    
    print("="*80)
    print("🧪 端到端测试 - DeepResearch 完整流程")
    print("="*80)

    # 检查 API Key（支持 LLM_API_KEY 或 OPENAI_API_KEY）
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    provider = os.getenv("LLM_PROVIDER", "openai")

    if not api_key:
        print("\n⚠️  LLM_API_KEY 或 OPENAI_API_KEY 未设置，将跳过 LLM 调用")
        print("   如需完整测试，请设置:")
        print("   export LLM_PROVIDER=qwen")
        print("   export LLM_API_KEY='your-api-key'")
        print("\n📍 将只测试数据抓取部分...\n")
        use_llm = False
    else:
        print(f"\n✅ API Key 已设置")
        print(f"   提供商: {provider}")
        use_llm = True
    
    # 定义测试参数
    keyword = "standing desk"
    market = "US"
    competitors = [
        {
            "brand": "uplift",
            "url": "https://www.upliftdesk.com/uplift-v2-standing-desk-v2-or-v2-commercial/"
        },
        {
            "brand": "vari",
            "url": "https://www.vari.com/electric-standing-desk-60x30/FD-ESD6030.html"
        },
    ]
    
    print(f"\n📋 测试参数:")
    print(f"   关键词: {keyword}")
    print(f"   市场: {market}")
    print(f"   竞品数量: {len(competitors)}")
    for comp in competitors:
        print(f"      - {comp['brand']}: {comp['url'][:60]}...")
    
    try:
        if use_llm:
            # 完整测试（包括 LLM）
            print(f"\n{'='*80}")
            print("🚀 开始完整测试（包括 LLM）...")
            print(f"{'='*80}\n")
            
            orchestrator = ResearchOrchestrator(api_key)
            
            report = await orchestrator.run_research(
                keyword=keyword,
                market=market,
                competitors=competitors
            )
            
            await orchestrator.cleanup()
            
            # 显示结果
            print(f"\n{'='*80}")
            print("✅ 测试完成！")
            print(f"{'='*80}\n")
            
            print("📊 报告摘要:")
            metadata = report.get("metadata", {})
            print(f"   生成时间: {metadata.get('generated_at', 'N/A')}")
            print(f"   耗时: {metadata.get('duration_seconds', 0):.1f} 秒")
            
            efficiency = report.get("efficiency_comparison", {})
            print(f"\n⚡ 效率对比:")
            print(f"   人工: {efficiency.get('manual_hours', 0)} 小时")
            print(f"   工具: {efficiency.get('tool_seconds', 0):.1f} 秒")
            print(f"   提速: {efficiency.get('speedup', 0):.0f}x")
            
            comparison = report.get("comparison_table", {})
            if comparison and "error" not in comparison:
                print(f"\n📋 竞品对比表:")
                print(f"   {json.dumps(comparison, indent=2, ensure_ascii=False)[:300]}...")
            
            action_plan = report.get("action_plan", {})
            if action_plan and "error" not in action_plan:
                print(f"\n🎯 行动计划:")
                print(f"   {json.dumps(action_plan, indent=2, ensure_ascii=False)[:300]}...")
            
            # 保存完整报告
            with open("test_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 完整报告已保存到: test_report.json")
            
        else:
            # 仅测试数据抓取
            print(f"\n{'='*80}")
            print("🔍 测试数据抓取...")
            print(f"{'='*80}\n")
            
            from mcp_servers.ecommerce import EcommerceMCPServer
            
            ecommerce_server = EcommerceMCPServer()
            
            product_data = []
            for competitor in competitors:
                brand = competitor["brand"]
                url = competitor["url"]
                
                print(f"📦 抓取 {brand}...")
                
                result = await ecommerce_server.call_tool(
                    "get_product_info",
                    {"brand": brand, "url": url}
                )
                
                if result and len(result) > 0:
                    data = json.loads(result[0].text)
                    product_data.append(data)
                    
                    print(f"   ✅ 标题: {data.get('title', 'N/A')[:60]}...")
                    print(f"   ✅ 价格: ${data.get('price', 'N/A')}")
                    print()
            
            # 清理
            for scraper in ecommerce_server.scrapers.values():
                await scraper._close_browser()
            
            print(f"{'='*80}")
            print(f"✅ 数据抓取测试完成！成功: {len(product_data)}/{len(competitors)}")
            print(f"{'='*80}")
            
            # 保存数据
            with open("test_product_data.json", "w", encoding="utf-8") as f:
                json.dump(product_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 产品数据已保存到: test_product_data.json")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print(f"\n{'='*80}")

if __name__ == "__main__":
    success = asyncio.run(test_end_to_end())
    sys.exit(0 if success else 1)

