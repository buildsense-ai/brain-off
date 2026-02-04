#!/usr/bin/env python3
"""
详细调试 CLI 流程
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database.session import get_db
from src.core.agent.memory_driven_agent import MemoryDrivenAgent
from src.skills.initialize import initialize_all_tools


async def test_with_debug():
    print("=" * 60)
    print("详细调试测试")
    print("=" * 60)
    print()

    # 初始化工具
    initialize_all_tools()

    # 创建 Agent
    async for db in get_db():
        agent = MemoryDrivenAgent(db, use_reasoner=False, fixed_skill_id="cost")
        print("✅ Agent 创建成功")
        print()

        # 测试消息
        test_message = "列出workspace中的所有CAD文件"
        print(f"用户: {test_message}")
        print()

        # 详细的回调函数
        def stream_callback(chunk_type, content):
            print(f"\n[DEBUG] Type: {chunk_type}, Content: {repr(content[:100] if len(content) > 100 else content)}")

            if chunk_type == "text":
                print(content, end="", flush=True)

        try:
            result = await agent.process_message(
                test_message,
                stream_callback=stream_callback
            )
            print(f"\n\n[DEBUG] Final result: {result}")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        break


if __name__ == "__main__":
    asyncio.run(test_with_debug())
