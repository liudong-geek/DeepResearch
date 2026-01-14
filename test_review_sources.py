#!/usr/bin/env python3
"""测试评论洞察的溯源信息"""

import asyncio
import sys
import json
import os
sys.path.insert(0, "backend")

# 设置临时 API key（用于测试）
os.environ['LLM_API_KEY'] = 'test-key-for-structure-validation'

from orchestrator import ResearchOrchestrator


async def test_review_sources():
    """测试评论洞察是否包含溯源信息"""

    print("🧪 测试评论洞察溯源信息\n")

    # 初始化 Orchestrator
    orchestrator = ResearchOrchestrator()
    
    # 模拟评论数据（带溯源信息）
    review_data = [
        {
            "company_name": "Uplift Desk",
            "overall_rating": 4.5,
            "total_reviews": 1234,
            "reviews": [
                {
                    "rating": 5,
                    "title": "Great desk!",
                    "text": "Very stable and easy to assemble. Love the height adjustment."
                },
                {
                    "rating": 4,
                    "title": "Good but pricey",
                    "text": "Quality is excellent but the price is a bit high."
                },
                {
                    "rating": 2,
                    "title": "Wobbly",
                    "text": "The desk wobbles when fully extended. Customer service was slow."
                }
            ],
            "_source": {
                "type": "trustpilot_reviews",
                "url": "https://www.trustpilot.com/review/upliftdesk.com",
                "brand": "Uplift",
                "extracted_at": "2026-01-15T00:00:00",
                "data_points": ["reviews", "overall_rating", "total_reviews"]
            }
        },
        {
            "company_name": "Fully Jarvis",
            "overall_rating": 4.3,
            "total_reviews": 987,
            "reviews": [
                {
                    "rating": 5,
                    "title": "Perfect!",
                    "text": "Smooth motor, very quiet. Assembly was straightforward."
                },
                {
                    "rating": 3,
                    "title": "Decent",
                    "text": "Works well but had some shipping damage."
                }
            ],
            "_source": {
                "type": "trustpilot_reviews",
                "url": "https://www.trustpilot.com/review/fully.com",
                "brand": "Jarvis",
                "extracted_at": "2026-01-15T00:00:00",
                "data_points": ["reviews", "overall_rating", "total_reviews"]
            }
        }
    ]
    
    print("=" * 80)
    print("调用 _analyze_reviews 方法...")
    print("=" * 80)
    
    try:
        # 调用评论分析
        result = await orchestrator._analyze_reviews(review_data, reddit_data=None)
        
        print("\n✅ 分析完成！\n")
        
        # 检查溯源信息
        if '_sources' in result:
            print("📍 溯源信息:")
            for source in result['_sources']:
                print(f"\n  类型: {source['type']}")
                print(f"  品牌: {source.get('brand', 'N/A')}")
                print(f"  URL: {source['url']}")
                print(f"  评论数: {source.get('review_count', 'N/A')}")
                print(f"  平均评分: {source.get('overall_rating', 'N/A')}")
        else:
            print("❌ 缺少 _sources 字段")
        
        # 检查元数据
        if '_metadata' in result:
            print("\n📊 元数据:")
            metadata = result['_metadata']
            print(f"  总评论数: {metadata.get('total_reviews_analyzed', 0)}")
            print(f"  Reddit 帖子数: {metadata.get('total_reddit_posts', 0)}")
            print(f"  分析品牌: {', '.join(metadata.get('brands_analyzed', []))}")
        else:
            print("❌ 缺少 _metadata 字段")
        
        # 显示主题和洞察
        print(f"\n🏷️  主题数: {len(result.get('topics', []))}")
        print(f"✅ 正面洞察: {len(result.get('positive_insights', []))}")
        print(f"⚠️  负面洞察: {len(result.get('negative_insights', []))}")
        
        # 保存完整结果
        print("\n保存完整结果到 test_review_sources_result.json")
        with open("test_review_sources_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_review_sources())

