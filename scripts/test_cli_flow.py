#!/usr/bin/env python3
"""
测试 CLI 完整流程
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database.session import get_db
from src.core.agent.memory_driven_agent import MemoryDrivenAgent
from src.skills.initialize import initialize_all_tools


async def test_cli_flow():
    print("=" * 60)
    print("测试 CLI 完整流程")
    print("=" * 60)
    print()

    # 1. 初始化工具
    print("📋 步骤 1: 初始化工具")
    initialize_all_tools()
    print()

    # 2. 创建 Agent（固定 cost skill）
    print("📋 步骤 2: 创建 Agent（固定 cost skill）")
    async for db in get_db():
        agent = MemoryDrivenAgent(db, use_reasoner=False, fixed_skill_id="cost")
        print("✅ Agent 创建成功")
        print()

        # 3. 测试消息处理
        print("📋 步骤 3: 测试消息处理")
        print("-" * 60)
        test_message = "列出workspace中的所有CAD文件"
        print(f"用户: {test_message}")
        print()
        print("助手: ", end="", flush=True)

        def stream_callback(chunk):
            if chunk.get("type") == "content":
                print(chunk.get("content", ""), end="", flush=True)

        try:
            result = await agent.process_message(
                test_message,
                stream_callback=stream_callback
            )
            print("\n")
            print("✅ 消息处理成功")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        break

    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_cli_flow())
