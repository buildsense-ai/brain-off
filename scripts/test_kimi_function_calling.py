"""
测试 Kimi 2.5 的 function calling 功能
"""
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_kimi_function_calling():
    """测试 Kimi 是否支持 function calling"""

    client = AsyncOpenAI(
        api_key=os.getenv("VISION_MODEL_API_KEY"),
        base_url=os.getenv("VISION_MODEL_BASE_URL")
    )

    # 定义一个简单的工具
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取指定城市的天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称，例如：北京、上海"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": "你是一个智能助手。"},
        {"role": "user", "content": "北京今天天气怎么样？"}
    ]

    print("="*60)
    print("测试 Kimi 2.5 Function Calling")
    print("="*60)
    print(f"\n[API Key] {os.getenv('VISION_MODEL_API_KEY')[:20]}...")
    print(f"[Base URL] {os.getenv('VISION_MODEL_BASE_URL')}")
    print(f"[Model] kimi-k2.5")
    print(f"\n[用户消息] {messages[1]['content']}")
    print(f"[工具定义] {tools[0]['function']['name']}")

    try:
        response = await client.chat.completions.create(
            model="kimi-k2.5",
            messages=messages,
            tools=tools,
            temperature=1.0
        )

        print(f"\n[响应状态] 成功")
        print(f"[Choices 数量] {len(response.choices)}")

        if response.choices:
            message = response.choices[0].message
            print(f"[Content] {message.content}")
            print(f"[Tool Calls] {message.tool_calls}")

            if message.tool_calls:
                print(f"\n✅ Kimi 调用了工具！")
                for tc in message.tool_calls:
                    print(f"  - 工具名: {tc.function.name}")
                    print(f"  - 参数: {tc.function.arguments}")
            else:
                print(f"\n❌ Kimi 没有调用工具")
                print(f"   响应内容: {message.content[:200]}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kimi_function_calling())
