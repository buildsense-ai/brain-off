"""
测试新架构 - 简单的端到端测试
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database.session import get_db
from src.core.agent.memory_driven_agent import MemoryDrivenAgent
from src.skills.todo.setup import initialize_todo_tools


async def test_agent():
    """测试 agent 基本功能"""

    # 1. 初始化工具
    print("🔧 初始化工具...")
    initialize_todo_tools()
    print("✅ 工具初始化完成\n")

    # 2. 创建 agent
    print("🤖 创建 Agent...")
    async for db in get_db():
        agent = MemoryDrivenAgent(db, use_reasoner=False)
        print("✅ Agent 创建完成\n")

        # 3. 测试简单对话
        print("💬 测试 1: 简单问候")
        result = await agent.process_message("你好")
        print(f"结果: {result}")
        if result.get('success'):
            print(f"回复: {result.get('text', 'N/A')}")
            print(f"Skill: {result.get('metadata', {}).get('skill_id', 'None')}\n")
        else:
            print(f"错误: {result.get('error', 'Unknown error')}\n")
            return

        # 4. 测试任务创建
        print("💬 测试 2: 创建任务")
        result = await agent.process_message("创建任务：测试新架构")
        if result.get('success'):
            print(f"回复: {result.get('text', 'N/A')}")
            print(f"Skill: {result.get('metadata', {}).get('skill_id', 'None')}")
            print(f"工具调用: {len(result.get('metadata', {}).get('tool_calls', []))} 次\n")
        else:
            print(f"错误: {result.get('error', 'Unknown error')}\n")
            return

        print("✅ 所有测试通过！")
        break


if __name__ == "__main__":
    asyncio.run(test_agent())
