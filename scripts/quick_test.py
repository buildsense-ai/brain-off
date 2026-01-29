"""
快速测试 - 验证核心功能

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/quick_test.py
"""
import asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.connection import engine
from src.agent.memory_driven_agent import MemoryDrivenAgent


async def quick_test():
    """快速测试核心功能"""
    print("=== 快速功能测试 ===\n")

    async with AsyncSession(engine) as session:
        agent = MemoryDrivenAgent(db=session)
        session_id = None

        # 测试消息列表
        test_messages = [
            "你好",
            "创建一个学习 Python 的任务",
            "再创建一个写论文的任务，优先级高",
            "列出所有任务",
            "把学习 Python 改为进行中",
        ]

        for i, msg in enumerate(test_messages, 1):
            print(f"\n{'='*50}")
            print(f"[{i}] 用户: {msg}")
            print(f"{'='*50}")

            result = await agent.process_message(
                user_message=msg,
                session_id=session_id
            )

            if session_id is None:
                session_id = UUID(result.get("session_id"))

            if result.get("success"):
                print(f"\n✅ Agent: {result.get('text', '')[:300]}...")
                print(f"迭代: {result.get('iterations', 0)}")
            else:
                print(f"\n❌ 错误: {result.get('error')}")

        # 检查数据库状态
        print(f"\n{'='*50}")
        print("📊 数据库状态")
        print(f"{'='*50}")

        result = await session.execute(text("SELECT COUNT(*) FROM tasks"))
        print(f"任务数: {result.scalar()}")

        result = await session.execute(text("SELECT COUNT(*) FROM mem_source"))
        print(f"对话记录: {result.scalar()}")

        result = await session.execute(text("SELECT COUNT(*) FROM facts"))
        print(f"事实记忆: {result.scalar()}")

        print("\n✅ 测试完成！")


if __name__ == "__main__":
    asyncio.run(quick_test())
