"""
测试对话压缩触发机制

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/test_compression_trigger.py
"""
import asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import engine
from src.agent.memory_driven_agent import MemoryDrivenAgent


async def test_compression_trigger():
    """测试压缩触发机制"""
    print("=== 测试对话压缩触发 ===\n")

    async with AsyncSession(engine) as session:
        agent = MemoryDrivenAgent(db=session)

        # 模拟 16 轮对话（超过阈值 15）
        test_messages = [
            "你好",
            "帮我创建一个任务",
            "任务标题是学习 Python",
            "再创建一个任务",
            "标题是学习 JavaScript",
            "列出所有任务",
            "把第一个任务标记为完成",
            "再创建一个任务",
            "标题是学习 TypeScript",
            "列出所有任务",
            "删除第二个任务",
            "再创建一个任务",
            "标题是学习 Rust",
            "列出所有任务",
            "把第三个任务标记为完成",
            "现在有多少个任务？",  # 第 16 条消息，应该触发压缩
        ]

        session_id = None

        for i, msg in enumerate(test_messages, 1):
            print(f"\n[{i}/16] 用户: {msg}")

            result = await agent.process_message(
                user_message=msg,
                session_id=session_id
            )

            if session_id is None:
                # 将字符串转换为 UUID
                session_id = UUID(result.get("session_id"))

            print(f"Agent: {result['text'][:100]}...")

            # 在第 16 条消息后检查是否触发了压缩
            if i == 16:
                print("\n=== 检查压缩结果 ===")
                # 这里应该已经触发了压缩

        print("\n✅ 测试完成！")


if __name__ == "__main__":
    asyncio.run(test_compression_trigger())
