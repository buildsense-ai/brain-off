"""
测试记忆驱动 Agent

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/test_memory_driven_agent.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.connection import engine
from src.agent.memory_driven_agent import MemoryDrivenAgent


async def test_basic_conversation():
    """测试基础对话"""
    print("=== 测试记忆驱动 Agent ===\n")

    async with AsyncSession(engine) as session:
        agent = MemoryDrivenAgent(db=session)

        # 测试消息
        test_messages = [
            "帮我创建一个学习 Python 的任务",
            "列出所有任务",
        ]

        session_id = None

        for i, msg in enumerate(test_messages, 1):
            print(f"\n[{i}] 用户: {msg}")

            result = await agent.process_message(
                user_message=msg,
                session_id=session_id
            )

            if session_id is None:
                from uuid import UUID
                session_id = UUID(result.get("session_id"))

            # 先打印完整结果看看
            print(f"结果: {result}")

            if result.get('success'):
                print(f"Agent: {result.get('text', '')[:200]}...")
                print(f"迭代次数: {result.get('iterations', 0)}")
            else:
                print(f"错误: {result.get('error', 'Unknown error')}")

        print("\n✅ 测试完成！")


if __name__ == "__main__":
    asyncio.run(test_basic_conversation())
