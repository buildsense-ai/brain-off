"""
数据库初始化脚本 - 创建所有表并初始化 skills

运行方式：
python scripts/init_new_db.py
"""
import asyncio
from src.infrastructure.database.connection import engine
from src.infrastructure.database.models import Base


async def init_database():
    """初始化数据库"""

    print("🗑️  删除所有旧表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("✅ 旧表已删除")

    print("\n📦 创建所有新表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ 新表已创建")

    print("\n🎯 初始化 skills...")
    await init_skills()

    print("\n✅ 数据库初始化完成！")


async def init_skills():
    """初始化默认的 skills"""
    from src.infrastructure.database.session import get_session
    from src.core.skills.skill_service import SkillService

    skills_data = [
        {
            "skill_id": "todo",
            "name": "任务管理",
            "prompt_template": """## 任务管理技能（GTD 方法论）

### 任务状态
brainstorm（想法）→ inbox（待处理）→ active（进行中）→ completed（完成）
其他：waiting（等待）、someday（未来）、archived（归档）

### 核心规则
1. 用户要 1 个任务就创建 1 个，不要自作主张创建多个
2. 创建前先搜索，避免重复
3. 发现重复询问："已有相同任务，是否删除重复的？"

### CLI 输出规则
1. 工具调用后只需简短确认，不要重复工具已显示的信息
2. 不要输出任务 ID (UUID)
3. 不要使用 Markdown 格式（**粗体**、*斜体*、`代码`、- 列表）
4. 列出任务时使用纯文本，一行一个关键信息

示例 - 创建任务：
❌ 错误: "已创建任务：学习 Python\n任务 ID: xxx\n状态: inbox\n优先级: medium"
✅ 正确: "已创建任务"学习 Python"，状态为待处理"

示例 - 列出任务：
❌ 错误: "1. **学习 Python** (状态：待处理)\n   - 描述：xxx"
✅ 正确: "1. 学习 Python\n   状态: 待处理  优先级: 中\n   学习 Python 编程基础"
""",
            "tool_set": ["database_operation", "search"]
        }
    ]

    async with get_session() as db:
        skill_service = SkillService(db)
        for skill_data in skills_data:
            print(f"  - 创建 skill: {skill_data['name']}")
            await skill_service.create_skill(**skill_data)

    print("✅ Skills 初始化完成")


if __name__ == "__main__":
    asyncio.run(init_database())
