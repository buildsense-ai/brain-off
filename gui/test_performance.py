"""
测试性能追踪功能
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database.session import get_db
from src.core.agent.memory_driven_agent import MemoryDrivenAgent
from src.core.utils.performance_tracker import PerformanceTracker


async def test_performance_tracking():
    """测试性能追踪功能"""
    print("🧪 测试性能追踪功能\n")

    async for db in get_db():
        agent = MemoryDrivenAgent(db, use_reasoner=False)

        # 发送测试消息
        print("📤 发送测试消息...")
        response = await agent.process_message(
            user_message="你好，请介绍一下你自己",
            session_id="test_perf_123"
        )

        await db.commit()

        if response["success"]:
            print(f"\n✅ 消息处理成功")
            print(f"📝 响应: {response['text'][:100]}...\n")
        else:
            print(f"\n❌ 消息处理失败: {response.get('error')}\n")

        # 获取性能追踪数据
        print("=" * 50)
        print("📊 性能追踪摘要")
        print("=" * 50)

        requests = PerformanceTracker.get_recent_requests(limit=1)
        if requests:
            req = requests[0]
            print(f"\n请求 ID: {req.request_id}")
            print(f"查询: {req.user_query}")
            print(f"总耗时: {req.total_duration:.2f}s\n")

            print("主流程步骤:")
            for step in req.sync_steps:
                status = "✅" if step.status == "completed" else "❌"
                duration = f"{step.duration:.2f}s" if step.duration else "N/A"
                print(f"  {status} {step.name}: {duration}")

            if req.async_steps:
                print("\n后台任务:")
                for step in req.async_steps:
                    status = "✅" if step.status == "completed" else "❌"
                    duration = f"{step.duration:.2f}s" if step.duration else "N/A"
                    print(f"  {status} {step.name}: {duration}")

        return response["success"]


if __name__ == "__main__":
    success = asyncio.run(test_performance_tracking())
    sys.exit(0 if success else 1)
