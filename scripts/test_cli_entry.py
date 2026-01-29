"""
快速测试 CLI 入口

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/test_cli_entry.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.session import get_db
from src.agent.memory_driven_agent import MemoryDrivenAgent


async def test_cli_entry():
    """测试 CLI 入口是否正常"""
    print("=== 测试 CLI 入口 ===\n")

    async for db in get_db():
        agent = MemoryDrivenAgent(db, use_reasoner=False)

        # 测试消息
        result = await agent.process_message("你好")

        print(f"成功: {result.get('success')}")
        print(f"响应: {result.get('text', '')[:100]}...")

        await db.commit()
        break

    print("\n✅ CLI 入口测试完成！")


if __name__ == "__main__":
    asyncio.run(test_cli_entry())
