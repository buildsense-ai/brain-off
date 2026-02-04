"""
简化测试：验证 Kimi 多轮对话和工具调用
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


async def test_kimi_simple():
    """简单测试 Kimi 的工具调用"""
    print("="*60)
    print("Kimi 工具调用简化测试")
    print("="*60)

    # 初始化工具
    print("\n初始化工具...")
    initialize_all_tools()
    print()

    # 创建数据库会话
    db_path = project_root / "data" / "chatbot.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        agent = MemoryDrivenAgent(db=db, use_reasoner=False, fixed_skill_id="cost")

        # 第一轮：简单的文件列表查询
        print("[第1轮] 用户: 列出 cad_files 目录的文件")
        result1 = await agent.process_message(
            user_message="列出 cad_files 目录的文件",
            session_id=None
        )

        print(f"\n✓ 模型: {agent.llm_client.model}")
        print(f"✓ 支持视觉: {agent.llm_client.supports_vision}")
        print(f"✓ 成功: {result1.get('success')}")

        if result1.get('success'):
            tool_calls = result1.get('metadata', {}).get('tool_calls', [])
            print(f"✓ 工具调用: {len(tool_calls)} 次")

            if tool_calls:
                for tc in tool_calls:
                    print(f"  - {tc['name']}")

            response_text = result1.get('text', '')
            print(f"\n[响应预览] {response_text[:200]}...")
        else:
            print(f"✗ 错误: {result1.get('error')}")
            return

        print("\n" + "="*60)
        print("测试完成")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(test_kimi_simple())
