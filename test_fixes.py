#!/usr/bin/env python3
"""
测试修复是否生效
"""
import sys
import json

def test_api_model():
    """测试 API 模型是否包含新字段"""
    print("=" * 60)
    print("测试 1: API 模型修复")
    print("=" * 60)
    
    # 检查 ResearchResult 模型
    try:
        sys.path.insert(0, 'backend')
        from api.routes.research import ResearchResult
        
        # 检查字段
        fields = ResearchResult.model_fields
        
        print("✓ ResearchResult 模型字段:")
        for field_name in fields:
            print(f"  - {field_name}")
        
        # 检查新增字段
        required_fields = ['metadata', 'reddit_discussions']
        missing_fields = [f for f in required_fields if f not in fields]
        
        if missing_fields:
            print(f"\n✗ 缺少字段: {missing_fields}")
            return False
        else:
            print(f"\n✓ 所有必需字段都存在")
            return True
            
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        return False


def test_reddit_scraper():
    """测试 Reddit 爬虫改进"""
    print("\n" + "=" * 60)
    print("测试 2: Reddit 爬虫改进")
    print("=" * 60)
    
    try:
        sys.path.insert(0, 'backend')
        from mcp_servers.content.scrapers.reddit import RedditContentScraper
        
        # 检查 User-Agent 池
        if hasattr(RedditContentScraper, 'USER_AGENTS'):
            user_agents = RedditContentScraper.USER_AGENTS
            print(f"✓ User-Agent 池大小: {len(user_agents)}")
            print(f"  示例: {user_agents[0][:50]}...")
            return True
        else:
            print("✗ 缺少 USER_AGENTS 属性")
            return False
            
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_orchestrator_progress():
    """测试 Orchestrator 进度回调"""
    print("\n" + "=" * 60)
    print("测试 3: Orchestrator 进度回调")
    print("=" * 60)
    
    try:
        sys.path.insert(0, 'backend')
        from orchestrator.orchestrator import ResearchOrchestrator
        import inspect
        
        # 检查 run_research 方法签名
        sig = inspect.signature(ResearchOrchestrator.run_research)
        params = list(sig.parameters.keys())
        
        print(f"✓ run_research 方法参数:")
        for param in params:
            print(f"  - {param}")
        
        if 'progress_callback' in params:
            print(f"\n✓ 包含 progress_callback 参数")
            return True
        else:
            print(f"\n✗ 缺少 progress_callback 参数")
            return False
            
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n🔍 开始测试修复...\n")
    
    results = []
    
    # 运行测试
    results.append(("API 模型修复", test_api_model()))
    results.append(("Reddit 爬虫改进", test_reddit_scraper()))
    results.append(("Orchestrator 进度回调", test_orchestrator_progress()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

