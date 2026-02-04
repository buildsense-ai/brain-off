"""
测试模型切换和多轮对话

测试场景：
1. 无 skill - 默认 DeepSeek
2. cost skill - 自动切换到 Kimi 2.5（多模态）
3. 多轮对话 - 验证模型保持一致
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.agent.memory_driven_agent import MemoryDrivenAgent
from src.skills.initialize import initialize_all_tools


async def test_default_model():
    """测试默认模型（无 skill）"""
    print("\n" + "="*60)
    print("测试 1: 默认模型（无 skill）")
    print("="*60)

    # 创建数据库会话 - 使用绝对路径
    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "chatbot.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        agent = MemoryDrivenAgent(db=db, use_reasoner=False)

        # 第一轮对话
        print("\n[第1轮] 用户: 你好，请介绍一下你自己")
        result1 = await agent.process_message(
            user_message="你好，请介绍一下你自己",
            session_id=None
        )

        print(f"\n[成功] {result1.get('success', False)}")
        if not result1.get('success'):
            print(f"[错误] {result1.get('error', 'Unknown error')}")
            return None, None

        print(f"[模型] {agent.llm_client.model if agent.llm_client else 'None'}")
        print(f"[支持视觉] {agent.llm_client.supports_vision if agent.llm_client else 'N/A'}")
        print(f"[响应] {result1.get('text', 'No text')[:200]}...")

        # 第二轮对话（同一会话）
        print("\n[第2轮] 用户: 1+1等于几？")

        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result2 = await agent.process_message(
                    user_message="1+1等于几？",
                    session_id=result1['session_id']
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠️ 尝试 {attempt + 1} 失败，重试中...")
                    await asyncio.sleep(2)
                else:
                    print(f"  ❌ 所有重试失败: {str(e)[:100]}")
                    return result1, None

        if not result2.get('success'):
            print(f"[错误] {result2.get('error', 'Unknown error')}")
            return result1, None

        print(f"\n[模型] {agent.llm_client.model}")
        print(f"[响应] {result2.get('text', 'No text')[:200]}...")

        return result1, result2


async def test_cost_skill():
    """测试 cost skill（需要多模态）"""
    print("\n" + "="*60)
    print("测试 2: Cost Skill（多模态）")
    print("="*60)

    # 使用绝对路径
    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "chatbot.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        agent = MemoryDrivenAgent(db=db, use_reasoner=False, fixed_skill_id="cost")

        # 第一轮对话
        print("\n[第1轮] 用户: 列出工作目录的文件")
        result1 = await agent.process_message(
            user_message="列出工作目录的文件",
            session_id=None
        )

        print(f"\n[模型] {agent.llm_client.model if agent.llm_client else 'None'}")
        print(f"[支持视觉] {agent.llm_client.supports_vision if agent.llm_client else 'N/A'}")

        print(f"[成功] {result1.get('success', False)}")
        if not result1.get('success'):
            print(f"[错误] {result1.get('error', 'Unknown error')}")
            return None, None

        print(f"[工具调用] {len(result1.get('metadata', {}).get('tool_calls', []))} 次")

        if result1.get('metadata', {}).get('tool_calls'):
            for i, tool_call in enumerate(result1['metadata']['tool_calls'], 1):
                print(f"  {i}. {tool_call['name']}")

        print(f"[响应] {result1.get('text', 'No text')[:300]}...")

        # 第二轮对话（同一会话）
        print("\n[第2轮] 用户: 刚才找到了几个文件？")

        # 添加重试机制
        max_retries = 3
        result2 = None
        for attempt in range(max_retries):
            try:
                result2 = await agent.process_message(
                    user_message="刚才找到了几个文件？",
                    session_id=result1['session_id']
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠️ 尝试 {attempt + 1} 失败，重试中...")
                    await asyncio.sleep(2)
                else:
                    print(f"  ❌ 所有重试失败: {str(e)[:100]}")
                    return result1, None

        if not result2 or not result2.get('success'):
            print(f"[错误] {result2.get('error', 'Unknown error') if result2 else 'No response'}")
            return result1, None

        print(f"\n[模型] {agent.llm_client.model}")
        print(f"[工具调用] {len(result2.get('metadata', {}).get('tool_calls', []))} 次")
        print(f"[响应] {result2.get('text', 'No text')[:200]}...")

        return result1, result2


async def test_supervision_skill():
    """测试 supervision skill（也需要多模态）"""
    print("\n" + "="*60)
    print("测试 3: Supervision Skill（多模态）")
    print("="*60)

    # 使用绝对路径
    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "chatbot.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        agent = MemoryDrivenAgent(db=db, use_reasoner=False, fixed_skill_id="supervision")

        # 第一轮对话
        print("\n[第1轮] 用户: 列出工作目录的文件")
        result1 = await agent.process_message(
            user_message="列出工作目录的文件",
            session_id=None
        )

        print(f"\n[模型] {agent.llm_client.model if agent.llm_client else 'None'}")
        print(f"[支持视觉] {agent.llm_client.supports_vision if agent.llm_client else 'N/A'}")

        print(f"[成功] {result1.get('success', False)}")
        if not result1.get('success'):
            print(f"[错误] {result1.get('error', 'Unknown error')}")
            return None

        print(f"[工具调用] {len(result1.get('metadata', {}).get('tool_calls', []))} 次")
        print(f"[响应] {result1.get('text', 'No text')[:200]}...")

        return result1


async def main():
    """运行所有测试"""

    # 初始化所有工具
    print("初始化工具...")
    initialize_all_tools()
    print()

    try:
        # 测试 1: 默认模型
        await test_default_model()

        # 测试 2: Cost skill
        await test_cost_skill()

        # 测试 3: Supervision skill
        await test_supervision_skill()

        print("\n" + "="*60)
        print("所有测试完成")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
