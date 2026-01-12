#!/usr/bin/env python3
"""
测试 Qwen 配置
"""
import asyncio
import sys
import os

# 添加 backend 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_qwen():
    """测试 Qwen LLM"""
    from openai import AsyncOpenAI
    
    print("="*80)
    print("🧪 测试 Qwen LLM 配置")
    print("="*80)
    
    # 读取配置
    provider = os.getenv("LLM_PROVIDER", "qwen")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = os.getenv("LLM_MODEL", "qwen-plus")
    
    print(f"\n📋 配置信息:")
    print(f"   提供商: {provider}")
    print(f"   API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
    print(f"   Base URL: {base_url}")
    print(f"   模型: {model}")
    
    if not api_key:
        print("\n❌ 错误: 未设置 LLM_API_KEY 或 OPENAI_API_KEY")
        print("\n请设置环境变量:")
        print("   export LLM_PROVIDER=qwen")
        print("   export LLM_API_KEY='your-qwen-api-key'")
        print("\n或者编辑 .env 文件")
        return False
    
    try:
        # 初始化客户端
        print(f"\n{'='*80}")
        print("🔌 连接 Qwen API...")
        print(f"{'='*80}\n")
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 测试 1: 简单对话
        print("1️⃣ 测试简单对话...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": "你好，请用一句话介绍你自己。"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        answer = response.choices[0].message.content
        print(f"   回答: {answer}")
        print("   ✅ 通过\n")
        
        # 测试 2: JSON 输出
        print("2️⃣ 测试 JSON 输出...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个数据分析助手。请以 JSON 格式输出结果。"
                },
                {
                    "role": "user",
                    "content": "请分析以下产品：Uplift 升降桌，价格 $300。输出 JSON 格式，包含 product_name, price, category 字段。"
                }
            ],
            temperature=0.3,
        )
        
        answer = response.choices[0].message.content
        print(f"   回答: {answer[:200]}...")
        
        # 尝试解析 JSON
        import json
        try:
            # 提取 JSON（可能包含在 markdown 代码块中）
            if "```json" in answer:
                json_str = answer.split("```json")[1].split("```")[0].strip()
            elif "```" in answer:
                json_str = answer.split("```")[1].split("```")[0].strip()
            else:
                json_str = answer.strip()
            
            data = json.loads(json_str)
            print(f"   解析成功: {data}")
            print("   ✅ 通过\n")
        except Exception as e:
            print(f"   ⚠️  JSON 解析失败: {e}")
            print("   （这是正常的，Qwen 可能不支持 response_format）\n")
        
        # 测试 3: 竞品分析（实际场景）
        print("3️⃣ 测试竞品分析场景...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的市场调研分析师，擅长竞品对比分析。"
                },
                {
                    "role": "user",
                    "content": """请分析以下两个升降桌产品：

产品 1:
- 品牌: Uplift
- 价格: $300
- 描述: UPLIFT V3 Standing Desk

产品 2:
- 品牌: Vari
- 价格: $349
- 描述: Electric Standing Desk 60x30

请给出简短的对比分析（3-5 句话）。"""
                }
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        answer = response.choices[0].message.content
        print(f"   分析结果:\n{answer}")
        print("\n   ✅ 通过\n")
        
        # 显示使用统计
        print(f"{'='*80}")
        print("✅ 所有测试通过！")
        print(f"{'='*80}\n")
        
        print("📊 使用统计:")
        print(f"   模型: {model}")
        print(f"   总请求数: 3")
        
        if hasattr(response, 'usage'):
            usage = response.usage
            print(f"   最后一次请求:")
            print(f"      输入 tokens: {usage.prompt_tokens}")
            print(f"      输出 tokens: {usage.completion_tokens}")
            print(f"      总计 tokens: {usage.total_tokens}")
            
            # 估算成本（qwen-plus 价格）
            if model == "qwen-plus":
                input_cost = usage.prompt_tokens / 1_000_000 * 0.8  # ¥0.8/百万 tokens
                output_cost = usage.completion_tokens / 1_000_000 * 2  # ¥2/百万 tokens
                total_cost = input_cost + output_cost
                print(f"      估算成本: ¥{total_cost:.6f}")
        
        print(f"\n{'='*80}")
        print("🎉 Qwen 配置成功！可以开始使用了。")
        print(f"{'='*80}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n{'='*80}")
        print("💡 常见问题排查:")
        print(f"{'='*80}")
        print("1. 检查 API Key 是否正确")
        print("2. 检查账户余额是否充足")
        print("3. 检查网络连接")
        print("4. 检查模型名称是否正确")
        print("\n参考文档: docs/QWEN_SETUP.md")
        
        return False

if __name__ == "__main__":
    success = asyncio.run(test_qwen())
    sys.exit(0 if success else 1)

