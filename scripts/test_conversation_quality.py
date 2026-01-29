"""
对话质量测试 - 测试 Agent 回复的自然度和有效性

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/test_conversation_quality.py
"""
import asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import engine
from src.agent.memory_driven_agent import MemoryDrivenAgent


async def test_conversation_quality():
    """测试对话质量"""
    print("=== 对话质量测试 ===\n")

    async with AsyncSession(engine) as session:
        agent = MemoryDrivenAgent(db=session)
        session_id = None

        # 场景 1: 自然对话流程
        print("\n" + "="*60)
        print("场景 1: 自然对话流程")
        print("="*60)

        conversations = [
            "你好",
            "我想学习 Python，但不知道从哪里开始",
            "好的，那就先创建一个学习 Python 基础的任务吧",
            "我还想学习数据分析",
            "列出我的所有学习任务",
        ]

        for i, msg in enumerate(conversations, 1):
            print(f"\n[{i}] 用户: {msg}")
            print("-" * 60)

            result = await agent.process_message(
                user_message=msg,
                session_id=session_id
            )

            if session_id is None:
                session_id = UUID(result.get("session_id"))

            if result.get("success"):
                print(f"Agent: {result.get('text', '')}")
                print(f"(迭代: {result.get('iterations', 0)})")
            else:
                print(f"❌ 错误: {result.get('error')}")

        # 场景 2: 模糊需求处理
        print("\n\n" + "="*60)
        print("场景 2: 模糊需求处理")
        print("="*60)

        session_id = None  # 重置会话

        conversations2 = [
            "我有个想法",
            "想做个项目",
            "嗯，关于 AI 的",
        ]

        for i, msg in enumerate(conversations2, 1):
            print(f"\n[{i}] 用户: {msg}")
            print("-" * 60)

            result = await agent.process_message(
                user_message=msg,
                session_id=session_id
            )

            if session_id is None:
                session_id = UUID(result.get("session_id"))

            if result.get("success"):
                print(f"Agent: {result.get('text', '')}")
                print(f"(迭代: {result.get('iterations', 0)})")
            else:
                print(f"❌ 错误: {result.get('error')}")

        # 场景 3: 任务管理操作
        print("\n\n" + "="*60)
        print("场景 3: 任务管理操作")
        print("="*60)

        session_id = None  # 重置会话

        conversations3 = [
            "创建任务：写周报",
            "创建任务：准备会议材料",
            "创建任务：写周报",  # 重复任务
            "列出所有任务",
        ]

        for i, msg in enumerate(conversations3, 1):
            print(f"\n[{i}] 用户: {msg}")
            print("-" * 60)

            result = await agent.process_message(
                user_message=msg,
                session_id=session_id
            )

            if session_id is None:
                session_id = UUID(result.get("session_id"))

            if result.get("success"):
                print(f"Agent: {result.get('text', '')}")
                print(f"(迭代: {result.get('iterations', 0)})")
            else:
                print(f"❌ 错误: {result.get('error')}")

        print("\n\n✅ 对话质量测试完成！")


if __name__ == "__main__":
    asyncio.run(test_conversation_quality())
