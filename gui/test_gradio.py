"""
快速测试 Gradio GUI 的基本功能
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database.session import get_db
from src.core.agent.memory_driven_agent import MemoryDrivenAgent


async def test_agent():
    """测试 Agent 基本功能"""
    print("🧪 测试 Agent 初始化...")

    async for db in get_db():
        agent = MemoryDrivenAgent(db, use_reasoner=False)
        print("✅ Agent 初始化成功")

        print("\n🧪 测试消息处理...")
        response = await agent.process_message(
            user_message="你好，这是一个测试消息",
            session_id="test_session_123"
        )

        await db.commit()

        if response["success"]:
            print(f"✅ 消息处理成功")
            print(f"📝 响应: {response['text'][:100]}...")
        else:
            print(f"❌ 消息处理失败: {response.get('error')}")

        return response["success"]


if __name__ == "__main__":
    success = asyncio.run(test_agent())
    sys.exit(0 if success else 1)
