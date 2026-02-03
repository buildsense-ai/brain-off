"""
测试记忆系统的基本功能

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/test_memory_system.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.connection import engine
from src.services.memory_service import MemoryService
from src.services.compression_service import CompressionService


async def test_memory_write():
    """测试记忆写入功能"""
    print("\n=== 测试 1: 记忆写入 ===")

    async with AsyncSession(engine) as session:
        memory_service = MemoryService(session)

        # 写入一段对话
        source_id = await memory_service.write_conversation(
            session_id="test_session_001",
            turn=0,
            speaker="user",
            content="帮我创建一个任务，学习两阶段路由",
            tool_calls=None,
            tool_results=None
        )

        print(f"✓ 写入对话，source_id: {source_id}")

        # 写入一个事实
        fact_id = await memory_service.write_fact(
            fact_text="用户想要学习两阶段路由技术",
            source_ids=[source_id],
            fact_type="user_preference",
            domain="learning",
            confidence=0.95
        )

        print(f"✓ 写入事实，fact_id: {fact_id}")


async def test_memory_retrieval():
    """测试记忆检索功能"""
    print("\n=== 测试 2: 记忆检索 ===")

    async with AsyncSession(engine) as session:
        memory_service = MemoryService(session)

        # 检索相关记忆
        memories = await memory_service.retrieve_memories(
            query="两阶段路由",
            top_k=5
        )

        print(f"\n检索到 {len(memories['facts'])} 个事实:")
        for fact in memories['facts']:
            print(f"  - [{fact['similarity']:.3f}] {fact['fact_text']}")
            print(f"    类型: {fact['fact_type']}, 领域: {fact['domain']}")

        print(f"\n检索到 {len(memories['sources'])} 个对话片段:")
        for source in memories['sources']:
            print(f"  - [{source['similarity']:.3f}] {source['speaker']}: {source['content'][:50]}...")


async def test_compression():
    """测试对话压缩和事实提取"""
    print("\n=== 测试 3: 对话压缩和事实提取 ===")

    async with AsyncSession(engine) as session:
        compression_service = CompressionService(session)

        # 模拟一段对话
        conversation_history = [
            {"role": "user", "content": "帮我创建一个任务"},
            {"role": "assistant", "content": "好的，请告诉我任务的标题"},
            {"role": "user", "content": "学习记忆驱动的技能系统"},
            {
                "role": "assistant",
                "content": "已创建任务",
                "tool_calls": [{"name": "create_task", "arguments": {"title": "学习记忆驱动的技能系统"}}]
            }
        ]

        # 执行压缩
        result = await compression_service.compact_and_memorize(
            conversation_history=conversation_history,
            session_id="test_session_002"
        )

        print(f"✓ 压缩完成")
        print(f"  - 写入对话片段: {result['sources_written']}")
        print(f"  - 提取事实数量: {result['facts_extracted']}")


async def main():
    """运行所有测试"""
    print("开始测试记忆系统...")

    try:
        # 测试 1: 写入
        await test_memory_write()

        # 测试 2: 检索
        await test_memory_retrieval()

        # 测试 3: 压缩
        await test_compression()

        # 再次检索，验证压缩后的数据
        print("\n=== 测试 4: 验证压缩后的数据 ===")
        await test_memory_retrieval()

        print("\n✅ 所有测试完成！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


