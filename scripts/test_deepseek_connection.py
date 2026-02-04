"""
测试 DeepSeek API 连接
"""
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_deepseek_basic():
    """测试 DeepSeek 基本连接"""
    print("="*60)
    print("测试 DeepSeek API 连接")
    print("="*60)

    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    print(f"\n[API Key] {api_key[:20] if api_key else 'None'}...")
    print(f"[Base URL] {base_url}")
    print(f"[Model] deepseek-chat")

    if not api_key:
        print("\n❌ 错误: DEEPSEEK_API_KEY 未配置")
        return

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # 测试1: 简单对话
    print("\n" + "-"*60)
    print("测试1: 简单对话（无工具）")
    print("-"*60)

    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个智能助手。"},
                {"role": "user", "content": "1+1等于几？"}
            ],
            temperature=0.7
        )

        print(f"✅ 连接成功")
        print(f"[响应] {response.choices[0].message.content}")

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 测试2: 带工具的对话
    print("\n" + "-"*60)
    print("测试2: 工具调用")
    print("-"*60)

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
                            "description": "城市名称"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个智能助手。"},
                {"role": "user", "content": "北京今天天气怎么样？"}
            ],
            tools=tools,
            temperature=0.7
        )

        print(f"✅ 请求成功")
        message = response.choices[0].message
        print(f"[Content] {message.content}")
        print(f"[Tool Calls] {message.tool_calls}")

        if message.tool_calls:
            print(f"\n✅ DeepSeek 调用了工具！")
            for tc in message.tool_calls:
                print(f"  - 工具名: {tc.function.name}")
                print(f"  - 参数: {tc.function.arguments}")
        else:
            print(f"\n⚠️ DeepSeek 没有调用工具")

    except Exception as e:
        print(f"❌ 工具调用失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_deepseek_basic())
