"""
测试 chat.py 的完整流程
包括 LLM 自动选择 skill 的逻辑
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.database.session import get_db
from src.core.agent.memory_driven_agent import MemoryDrivenAgent
from src.skills.initialize import initialize_all_tools


async def test_chat_flow():
    """测试完整的 chat 流程"""
    print("="*60)
    print("测试 Chat.py 完整流程")
    print("="*60)

    # 初始化工具
    print("\n初始化工具...")
    initialize_all_tools()
    print()

    # 获取数据库会话
    async for db in get_db():
        # 创建 agent（不指定 fixed_skill_id，让 LLM 自动选择）
        agent = MemoryDrivenAgent(db=db, use_reasoner=False)

        # 测试1: 通用对话（不应该触发 skill）
        print("-"*60)
        print("测试1: 通用对话（无 skill）")
        print("-"*60)
        print("[用户] 你好，请介绍一下你自己")

        try:
            result1 = await agent.process_message(
                user_message="你好，请介绍一下你自己",
                session_id=None
            )

            print(f"\n[成功] {result1.get('success')}")
            print(f"[模型] {agent.llm_client.model if agent.llm_client else 'None'}")
            print(f"[Skill ID] {result1.get('metadata', {}).get('skill_id', 'None')}")
            print(f"[推理] {result1.get('metadata', {}).get('reasoning', 'None')[:100]}...")
            print(f"[响应] {result1.get('text', 'No text')[:200]}...")

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        # 测试2: CAD 相关对话（应该触发 cost skill）
        print("\n" + "-"*60)
        print("测试2: CAD 相关对话（应触发 cost skill）")
        print("-"*60)
        print("[用户] 帮我分析一下 CAD 图纸")

        try:
            result2 = await agent.process_message(
                user_message="帮我分析一下 CAD 图纸",
                session_id=result1.get('session_id') if result1.get('success') else None
            )

            print(f"\n[成功] {result2.get('success')}")
            print(f"[模型] {agent.llm_client.model if agent.llm_client else 'None'}")
            print(f"[Skill ID] {result2.get('metadata', {}).get('skill_id', 'None')}")
            print(f"[推理] {result2.get('metadata', {}).get('reasoning', 'None')[:100]}...")
            print(f"[工具调用] {len(result2.get('metadata', {}).get('tool_calls', []))} 次")

        except Exception as e:
            print(f"\n❌ 错误: {e}")

        print("\n" + "="*60)
        print("测试完成")
        print("="*60)

        break  # 只使用第一个 db session


if __name__ == "__main__":
    asyncio.run(test_chat_flow())
