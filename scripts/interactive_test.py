"""
交互式测试 - 模拟真实用户对话场景

测试目标：
1. 基础任务管理（创建、查询、更新、删除）
2. 记忆系统（对话压缩、事实提取）
3. 技能识别和记忆检索
4. 重复任务检测和清理

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/interactive_test.py
"""
import asyncio
from uuid import UUID
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.connection import engine
from src.agent.memory_driven_agent import MemoryDrivenAgent


class TestScenario:
    """测试场景基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.messages: List[str] = []
        self.expectations: List[Dict[str, Any]] = []

    def add_message(self, message: str, expect: Optional[Dict[str, Any]] = None):
        """添加测试消息"""
        self.messages.append(message)
        if expect:
            self.expectations.append(expect)
        else:
            self.expectations.append({})


class InteractiveTester:
    """交互式测试器"""

    def __init__(self):
        self.session_id: Optional[UUID] = None
        self.agent: Optional[MemoryDrivenAgent] = None
        self.db: Optional[AsyncSession] = None

    async def setup(self):
        """初始化测试环境"""
        self.db = AsyncSession(engine)
        self.agent = MemoryDrivenAgent(db=self.db)
        print("✅ 测试环境初始化完成\n")

    async def teardown(self):
        """清理测试环境"""
        if self.db:
            await self.db.close()

    async def send_message(self, message: str, turn: int) -> Dict[str, Any]:
        """发送消息并获取响应"""
        print(f"\n{'='*60}")
        print(f"[轮次 {turn}] 用户: {message}")
        print(f"{'='*60}")

        result = await self.agent.process_message(
            user_message=message,
            session_id=self.session_id
        )

        if self.session_id is None and result.get("session_id"):
            self.session_id = UUID(result["session_id"])

        if result.get("success"):
            print(f"\n✅ Agent 响应:")
            print(result.get("text", ""))
            print(f"\n📊 迭代次数: {result.get('iterations', 0)}")
        else:
            print(f"\n❌ 错误: {result.get('error', 'Unknown error')}")

        return result

    async def check_database_state(self, description: str):
        """检查数据库状态"""
        print(f"\n{'─'*60}")
        print(f"📊 数据库状态检查: {description}")
        print(f"{'─'*60}")

        # 检查任务数量
        result = await self.db.execute(text("SELECT COUNT(*) FROM tasks"))
        task_count = result.scalar()
        print(f"任务总数: {task_count}")

        # 检查记忆数量
        result = await self.db.execute(text("SELECT COUNT(*) FROM mem_source"))
        source_count = result.scalar()
        print(f"对话记录: {source_count}")

        result = await self.db.execute(text("SELECT COUNT(*) FROM facts"))
        fact_count = result.scalar()
        print(f"事实记忆: {fact_count}")

        return {
            "tasks": task_count,
            "sources": source_count,
            "facts": fact_count
        }

    async def run_scenario(self, scenario: TestScenario):
        """运行测试场景"""
        print(f"\n{'#'*60}")
        print(f"# 测试场景: {scenario.name}")
        print(f"# 描述: {scenario.description}")
        print(f"{'#'*60}")

        for i, message in enumerate(scenario.messages, 1):
            result = await self.send_message(message, i)

            # 每 5 轮检查一次数据库状态
            if i % 5 == 0:
                await self.check_database_state(f"第 {i} 轮后")

            # 短暂延迟，模拟真实用户输入
            await asyncio.sleep(0.5)

        # 最终状态检查
        await self.check_database_state("场景结束")
        print(f"\n✅ 场景 '{scenario.name}' 完成\n")


def create_basic_scenario() -> TestScenario:
    """创建基础功能测试场景"""
    scenario = TestScenario(
        name="基础任务管理",
        description="测试任务的创建、查询、更新、删除功能"
    )

    # 第一阶段：创建任务
    scenario.add_message("你好")
    scenario.add_message("帮我创建一个学习 Python 的任务")
    scenario.add_message("再创建一个写论文的任务，优先级设为高")
    scenario.add_message("创建一个健身计划的想法")

    # 第二阶段：查询任务
    scenario.add_message("列出所有任务")
    scenario.add_message("有哪些高优先级的任务？")

    return scenario


def create_memory_scenario() -> TestScenario:
    """创建记忆系统测试场景（触发压缩）"""
    scenario = TestScenario(
        name="记忆系统测试",
        description="测试对话压缩和事实提取（16轮对话触发压缩）"
    )

    # 模拟 16+ 轮对话，触发压缩
    scenario.add_message("你好")
    scenario.add_message("创建任务：学习 Python")
    scenario.add_message("创建任务：学习 JavaScript")
    scenario.add_message("创建任务：写技术博客")
    scenario.add_message("列出所有任务")
    scenario.add_message("把学习 Python 标记为进行中")
    scenario.add_message("创建任务：阅读技术书籍")
    scenario.add_message("列出进行中的任务")
    scenario.add_message("创建任务：参加技术分享会")
    scenario.add_message("列出所有任务")
    scenario.add_message("把学习 JavaScript 标记为完成")
    scenario.add_message("创建任务：准备面试")
    scenario.add_message("列出已完成的任务")
    scenario.add_message("创建任务：优化代码性能")
    scenario.add_message("列出所有任务")
    scenario.add_message("现在有多少个任务？")  # 第 16 条，应该触发压缩

    return scenario


def create_skill_scenario() -> TestScenario:
    """创建技能识别测试场景"""
    scenario = TestScenario(
        name="技能识别和记忆检索",
        description="测试系统是否能识别不同技能领域并检索相关记忆"
    )

    # 混合不同领域的任务
    scenario.add_message("创建任务：写一篇关于 AI 的文章")  # writing
    scenario.add_message("创建任务：学习深度学习")  # learning
    scenario.add_message("创建任务：整理今天的待办事项")  # todo
    scenario.add_message("列出所有写作相关的任务")
    scenario.add_message("列出所有学习相关的任务")

    return scenario


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 开始交互式测试")
    print("="*60)

    tester = InteractiveTester()
    await tester.setup()

    try:
        # 场景 1: 基础功能测试
        scenario1 = create_basic_scenario()
        await tester.run_scenario(scenario1)

        # 重置会话，开始新场景
        tester.session_id = None

        # 场景 2: 记忆系统测试
        scenario2 = create_memory_scenario()
        await tester.run_scenario(scenario2)

        # 重置会话，开始新场景
        tester.session_id = None

        # 场景 3: 技能识别测试
        scenario3 = create_skill_scenario()
        await tester.run_scenario(scenario3)

        print("\n" + "="*60)
        print("✅ 所有测试场景完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await tester.teardown()


if __name__ == "__main__":
    asyncio.run(main())

