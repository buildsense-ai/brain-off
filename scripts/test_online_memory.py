"""
测试线上记忆接口集成

测试内容：
1. 存储消息到线上 API
2. 从线上 API 召回记忆
3. 验证数据格式
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.memory.online_memory_adapter import OnlineMemoryAdapter


async def test_store_message():
    """测试存储消息"""
    print("\n" + "="*60)
    print("测试 1: 存储消息到线上 API")
    print("="*60)

    adapter = OnlineMemoryAdapter(enabled=True)

    # 测试存储用户消息
    print("\n📝 存储用户消息...")
    result1 = await adapter.store_message(
        text="你好，我想了解一下 Python 的异步编程",
        user_id="test_user",
        session_id="test_session_001",
        role="user"
    )
    print(f"结果: {result1}")

    # 等待一下，让后台处理
    await asyncio.sleep(1)

    # 测试存储助手消息
    print("\n📝 存储助手消息...")
    result2 = await adapter.store_message(
        text="Python 的异步编程主要使用 asyncio 库，通过 async/await 语法实现非阻塞的并发操作。",
        user_id="test_user",
        session_id="test_session_001",
        role="assistant"
    )
    print(f"结果: {result2}")

    return result1, result2


async def test_recall_memories():
    """测试召回记忆"""
    print("\n" + "="*60)
    print("测试 2: 从线上 API 召回记忆")
    print("="*60)

    adapter = OnlineMemoryAdapter(enabled=True)

    # 测试基础召回
    print("\n🔍 测试基础召回...")
    memories = await adapter.recall_memories(
        query="Python 异步编程",
        top_k=3
    )

    print(f"\n召回 {len(memories)} 条记忆:")
    for i, mem in enumerate(memories, 1):
        print(f"\n记忆 {i}:")
        print(f"  内容: {mem['content'][:100]}...")
        print(f"  来源: {mem['source']}")
        print(f"  类型: {mem['type']}")

    # 测试启用图扩展的召回
    print("\n🔍 测试图扩展召回...")
    memories_with_graph = await adapter.recall_memories(
        query="Python 异步编程",
        top_k=3,
        enable_graph=True,
        max_hops=1
    )

    print(f"\n召回 {len(memories_with_graph)} 条记忆（含图扩展）")

    return memories


async def test_full_workflow():
    """测试完整工作流"""
    print("\n" + "="*60)
    print("测试 3: 完整工作流（存储 + 召回）")
    print("="*60)

    adapter = OnlineMemoryAdapter(enabled=True)

    # 1. 存储一些测试消息
    print("\n📝 存储测试对话...")
    await adapter.store_message(
        text="什么是 Docker？",
        user_id="test_user",
        session_id="test_session_002",
        role="user"
    )

    await adapter.store_message(
        text="Docker 是一个开源的容器化平台，可以将应用程序及其依赖打包成容器。",
        user_id="test_user",
        session_id="test_session_002",
        role="assistant"
    )

    # 等待后台处理
    print("⏳ 等待后台处理...")
    await asyncio.sleep(2)

    # 2. 召回相关记忆
    print("\n🔍 召回相关记忆...")
    memories = await adapter.recall_memories(
        query="Docker 容器",
        top_k=5
    )

    print(f"\n✅ 召回 {len(memories)} 条记忆")

    return memories


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("线上记忆接口集成测试")
    print("="*60)

    try:
        # 测试 1: 存储消息
        await test_store_message()

        # 等待一下
        await asyncio.sleep(2)

        # 测试 2: 召回记忆
        await test_recall_memories()

        # 测试 3: 完整工作流
        await test_full_workflow()

        print("\n" + "="*60)
        print("✅ 所有测试完成")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
