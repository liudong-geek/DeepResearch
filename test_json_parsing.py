#!/usr/bin/env python3
"""测试 JSON 解析修复"""

import json


def clean_json_response(content: str) -> str:
    """清理 LLM 返回的 JSON 响应（移除 markdown 格式）"""
    cleaned = content.strip()
    
    # 移除 markdown 代码块标记
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]  # 移除 ```json
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]  # 移除 ```
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]  # 移除结尾的 ```
    
    return cleaned.strip()


def test_json_parsing():
    """测试各种 JSON 格式"""
    
    # 测试用例 1: markdown 格式的 JSON
    test_case_1 = """```json
{
  "topics": [
    {
      "name": "客服",
      "count": 24,
      "percentage": 53.3,
      "sentiment": "mixed",
      "keywords": ["customer service", "support"]
    }
  ]
}
```"""
    
    # 测试用例 2: 纯 JSON
    test_case_2 = """{
  "topics": [
    {
      "name": "客服",
      "count": 24
    }
  ]
}"""
    
    # 测试用例 3: 只有 ``` 的格式
    test_case_3 = """```
{
  "topics": []
}
```"""
    
    test_cases = [
        ("Markdown JSON", test_case_1),
        ("Pure JSON", test_case_2),
        ("Simple Markdown", test_case_3)
    ]
    
    print("🧪 测试 JSON 解析修复\n")
    
    for name, content in test_cases:
        print(f"测试: {name}")
        print(f"原始内容长度: {len(content)} 字符")
        
        try:
            cleaned = clean_json_response(content)
            print(f"清理后长度: {len(cleaned)} 字符")
            
            parsed = json.loads(cleaned)
            print(f"✅ 解析成功: {list(parsed.keys())}")
            print(f"   Topics 数量: {len(parsed.get('topics', []))}")
        except json.JSONDecodeError as e:
            print(f"❌ 解析失败: {e}")
        
        print()


if __name__ == "__main__":
    test_json_parsing()

