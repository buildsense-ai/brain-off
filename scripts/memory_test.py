"""
记忆系统测试 - 触发对话压缩

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/memory_test.py
"""
import asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.connection import engine
from src.agent.memory_driven_agent import MemoryDrivenAgent


async def memory_test():
    """测试记忆系统（16轮对话触发压缩）"""
    print("=== 记忆系统测试 ===\n")

    async with AsyncSession(engine) as session:
        agent = MemoryDrivenAgent(db=session)
        session_id = None

        # 16 轮对话，触发压缩
        test_messages = [
            "你好",
            "创建任务：学习 Python",
            "创建任务：学习 JavaScript",
            "创建任务：写技术博客",
            "列出所有任务",
            "把学习 Python 改为进行中",
            "创建任务：阅读技术书籍",
            "列出进行中的任务",
            "创建任务：参加技术分享会",
            "列出所有任务",
            "把学习 JavaScript 改为完成",
            "创建任务：准备面试",
            "列出已完成的任务",
            "创建任务：优化代码性能",
            "列出所有任务",
            "现在有多少个任务？",  # 第 16 条，应该触发压缩
        ]

        for i, msg in enumerate(test_messages, 1):
            print(f"\n[{i}/16] 用户: {msg}")

            result = await agent.process_message(
                user_message=msg,
                session_id=session_id
            )

            if session_id is None:
                session_id = UUID(result.get("session_id"))

            if result.get("success"):
                response = result.get("text", "")
                print(f"Agent: {response[:150]}...")
            else:
                print(f"❌ 错误: {result.get('error')}")

            # 在第 16 轮后检查压缩
            if i == 16:
                print("\n" + "="*50)
                print("📊 检查压缩结果")
                print("="*50)

        # 最终数据库状态
        print("\n" + "="*50)
        print("📊 最终数据库状态")
        print("="*50)

        result = await session.execute(text("SELECT COUNT(*) FROM tasks"))
        print(f"任务数: {result.scalar()}")

        result = await session.execute(text("SELECT COUNT(*) FROM mem_source"))
        print(f"对话记录: {result.scalar()}")

        result = await session.execute(text("SELECT COUNT(*) FROM facts"))
        print(f"事实记忆: {result.scalar()}")

        print("\n✅ 记忆测试完成！")


if __name__ == "__main__":
    asyncio.run(memory_test())
