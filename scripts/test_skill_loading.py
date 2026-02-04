#!/usr/bin/env python3
"""
快速测试 Cost Skill 加载
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.skills.filesystem_skill_loader import FileSystemSkillLoader
from src.core.memory.embedding_service import EmbeddingService

def test_load_cost_skill():
    print("=" * 60)
    print("测试 Cost Skill 配置加载")
    print("=" * 60)

    # 创建加载器
    embedding_service = EmbeddingService()
    loader = FileSystemSkillLoader(
        skills_path="skills",
        embedding_service=embedding_service
    )

    # 加载 cost skill
    print("\n📋 加载 cost skill...")
    skill = loader.load_skill("cost")

    if skill:
        print(f"✅ Skill ID: {skill.id}")
        print(f"✅ Skill Name: {skill.name}")
        print(f"✅ Tools: {len(skill.tool_set)} 个")
        print(f"✅ Model Config: {skill.model_config}")
        print(f"✅ 加载成功！")
    else:
        print("❌ 加载失败")
        return False

    print("\n" + "=" * 60)
    print("✅ 测试通过")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_load_cost_skill()
    sys.exit(0 if success else 1)
