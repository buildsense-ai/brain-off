"""
测试 DeepSeek 的工具调用能力
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.agent.memory_driven_agent import MemoryDrivenAgent
from src.skills.initialize import initialize_all_tools


async def test_deepseek_default():
    """测试 DeepSeek 默认模型的工具调用"""
    print("="*60)
    print("测试 DeepSeek 工具调用（无 skill）")
    print("="*60)

    # 初始化工具
    print("\n初始化工具...")
    initialize_all_tools()

    # 创建数据库会话
    db_path = project_root / "data" / "chatbot.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        agent = MemoryDrivenAgent(db=db, use_reasoner=False)

        print("\n[测试] 用户: 帮我搜索一下Python相关的内容")
        result = await agent.process_message(
            user_message="帮我搜索一下Python相关的内容",
            session_id=None
        )

        print(f"\n[成功] {result.get('success', False)}")

        if not result.get('success'):
            print(f"[错误] {result.get('error', 'Unknown error')}")
            return None

        print(f"[模型] {agent.llm_client.model if agent.llm_client else 'None'}")
        print(f"[支持视觉] {agent.llm_client.supports_vision if agent.llm_client else 'N/A'}")
        print(f"[工具调用] {len(result.get('metadata', {}).get('tool_calls', []))} 次")

        if result.get('metadata', {}).get('tool_calls'):
            print("\n[调用的工具]:")
            for i, tool_call in enumerate(result['metadata']['tool_calls'], 1):
                print(f"  {i}. {tool_call['name']}")
                print(f"     参数: {tool_call['args']}")

        print(f"\n[响应] {result.get('text', 'No text')[:300]}...")

        return result


if __name__ == "__main__":
    asyncio.run(test_deepseek_default())
