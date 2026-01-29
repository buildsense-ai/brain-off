"""
测试记忆系统与 Main Agent 的集成

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/test_memory_integration.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import engine
from src.services.memory_service import MemoryService
from src.agent.memory_driven_agent import MemoryDrivenAgent


async def setup_test_memories():
    """设置测试用的记忆数据"""
    print("=== 设置测试记忆 ===")

    async with AsyncSession(engine) as session:
        memory_service = MemoryService(session)

        # 写入一些测试事实
        test_facts = [
            {
                "text": "用户喜欢使用 inbox 状态来管理新任务",
                "type": "user_preference",
                "domain": "todo"
            },
            {
                "text": "用户经常创建技术学习相关的任务",
                "type": "user_preference",
                "domain": "learning"
            },
            {
                "text": "用户习惯在创建任务后立即查看任务列表",
                "type": "workflow",
                "domain": "todo"
            }
        ]

        for fact in test_facts:
            await memory_service.write_fact(
                fact_text=fact["text"],
                source_ids=[],
                fact_type=fact["type"],
                domain=fact["domain"],
                confidence=0.9
            )
            print(f"✓ 写入事实: {fact['text'][:50]}...")


async def test_agent_with_memory():
    """测试 Main Agent 是否能使用记忆"""
    print("\n=== 测试 Main Agent 记忆集成 ===")

    async with AsyncSession(engine) as session:
        agent = MemoryDrivenAgent(db=session)

        # 测试查询
        test_query = "帮我创建一个学习 Python 的任务"
        print(f"\n用户查询: {test_query}")

        # 处理消息
        result = await agent.process_message(test_query)

        print(f"\nAgent 响应: {result['text'][:200]}...")
        print(f"成功: {result['success']}")
        print(f"迭代次数: {result['iterations']}")


async def main():
    """运行测试"""
    try:
        # 1. 设置测试记忆
        await setup_test_memories()

        # 2. 测试 Agent 集成
        await test_agent_with_memory()

        print("\n✅ 测试完成！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

