"""
测试技能记忆集成

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/test_skill_memory.py
"""
import asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import engine
from src.agent.memory_driven_agent import MemoryDrivenAgent


async def test_skill_memory_integration():
    """测试技能记忆集成"""
    print("=== 测试技能记忆集成 ===\n")

    async with AsyncSession(engine) as session:
        agent = MemoryDrivenAgent(db=session)

        # 测试对话序列
        test_messages = [
            "帮我创建一个学习 Python 的任务",
            "再创建一个学习 JavaScript 的任务",
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
                session_id = UUID(result.get("session_id"))

            print(f"Agent: {result['text'][:200]}...")
            print(f"成功: {result['success']}")

        print("\n✅ 测试完成！")


if __name__ == "__main__":
    asyncio.run(test_skill_memory_integration())
