"""
检查数据库中的 skill 数据
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.database.session import get_db
from src.core.skills.skill_service import SkillService


async def check_skills_in_db():
    """检查数据库中有哪些 skill"""
    print("="*60)
    print("检查数据库中的 Skill")
    print("="*60)

    async for db in get_db():
        skill_service = SkillService(db)

        # 获取所有 skill
        print("\n查询所有 skill...")

        # 直接查询数据库
        from src.infrastructure.database.models import Skill
        from sqlalchemy import select

        result = await db.execute(select(Skill))
        skills = result.scalars().all()

        print(f"\n数据库中的 skill 数量: {len(skills)}")

        if skills:
            print("\nSkill 列表:")
            for skill in skills:
                print(f"\n  ID: {skill.id}")
                print(f"  名称: {skill.name}")
                print(f"  描述: {skill.description[:100]}...")
                print(f"  工具数量: {len(skill.tool_set)}")
                print(f"  Embedding: {'有' if skill.embedding else '无'}")
        else:
            print("\n❌ 数据库中没有任何 skill！")
            print("   这就是为什么 LLM 检索不到 cost/supervision skill")

        break


if __name__ == "__main__":
    asyncio.run(check_skills_in_db())
