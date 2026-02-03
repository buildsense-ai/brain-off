#!/usr/bin/env python3
"""
Skill 开发工具

提供 skill 开发的完整生命周期管理：
- create: 创建新 skill
- test: 测试 skill
- register: 注册 skill 到数据库
- publish: 发布 skill 到生产环境
"""

import sys
import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SkillDevTool:
    """Skill 开发工具"""

    def __init__(self):
        self.project_root = project_root
        self.skills_dev_dir = self.project_root / "skills-dev"
        self.skills_prod_dir = self.project_root / "src" / "skills"
        self.template_dir = self.skills_dev_dir / "SKILL_TEMPLATE"

    def create(self, skill_id: str):
        """创建新 skill"""
        print(f"🚀 创建新 skill: {skill_id}\n")

        # 检查 skill_id 格式
        if not skill_id.replace("_", "").isalnum():
            print("❌ skill_id 只能包含字母、数字和下划线")
            return

        skill_dir = self.skills_dev_dir / skill_id

        # 检查是否已存在
        if skill_dir.exists():
            print(f"❌ Skill '{skill_id}' 已存在")
            return

        # 复制模板
        print(f"📁 从模板创建目录...")
        shutil.copytree(self.template_dir, skill_dir)

        # 更新 skill.yaml
        skill_yaml_path = skill_dir / "skill.yaml"
        with open(skill_yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        config["id"] = skill_id
        config["name"] = f"{skill_id} Skill"

        with open(skill_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)

        # 更新 README
        readme_path = skill_dir / "README.md"
        with open(readme_path, "r", encoding="utf-8") as f:
            readme = f.read()

        readme = readme.replace("your_skill_id", skill_id)
        readme = readme.replace("{Skill Name}", skill_id.title())

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)

        print(f"✅ Skill 创建成功！")
        print(f"\n📂 目录: {skill_dir}")
        print(f"\n下一步:")
        print(f"  1. 编辑 {skill_id}/skill.yaml - 配置 skill 信息")
        print(f"  2. 编辑 {skill_id}/prompt.md - 编写 prompt")
        print(f"  3. 编辑 {skill_id}/tools.py - 实现工具")
        print(f"  4. 运行测试: python scripts/skill_dev.py test {skill_id}")

    def test(self, skill_id: str):
        """测试 skill"""
        print(f"🧪 测试 skill: {skill_id}\n")

        skill_dir = self.skills_dev_dir / skill_id

        # 检查 skill 是否存在
        if not skill_dir.exists():
            print(f"❌ Skill '{skill_id}' 不存在")
            return

        # 运行单元测试
        test_tools_path = skill_dir / "tests" / "test_tools.py"
        if test_tools_path.exists():
            print("📝 运行单元测试...")
            os.system(f"cd {skill_dir} && python tests/test_tools.py")
        else:
            print("⚠️  未找到单元测试文件")

        print("\n" + "="*50 + "\n")

        # 运行集成测试
        test_integration_path = skill_dir / "tests" / "test_integration.py"
        if test_integration_path.exists():
            print("📝 运行集成测试...")
            os.system(f"cd {skill_dir} && python tests/test_integration.py")
        else:
            print("⚠️  未找到集成测试文件")

        print("\n✅ 测试完成！")

    def register(self, skill_id: str):
        """注册 skill 到数据库"""
        print(f"📝 注册 skill: {skill_id}\n")

        skill_dir = self.skills_dev_dir / skill_id

        # 检查 skill 是否存在
        if not skill_dir.exists():
            print(f"❌ Skill '{skill_id}' 不存在")
            return

        # 读取配置
        skill_yaml_path = skill_dir / "skill.yaml"
        with open(skill_yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 读取 prompt
        prompt_path = skill_dir / config.get("prompt_file", "prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        print(f"📄 Skill ID: {config['id']}")
        print(f"📄 Skill Name: {config['name']}")
        print(f"📄 Prompt 长度: {len(prompt_template)} 字符")

        # 生成 embedding
        print("\n🔄 生成 prompt embedding...")
        try:
            from src.core.memory.embedding_service import EmbeddingService
            from src.infrastructure.database.session import get_session

            session = get_session()
            embedding_service = EmbeddingService()

            embedding = embedding_service.generate_embedding(prompt_template)
            print(f"✅ Embedding 生成成功 (维度: {len(embedding)})")

            # 注册到数据库
            print("\n💾 注册到数据库...")
            from sqlalchemy import text

            # 检查是否已存在
            result = session.execute(
                text("SELECT id FROM skills WHERE id = :id"),
                {"id": config['id']}
            ).fetchone()

            if result:
                # 更新
                session.execute(
                    text("""
                        UPDATE skills
                        SET name = :name,
                            prompt_template = :prompt,
                            embedding = :embedding,
                            tool_set = :tools,
                            updated_at = NOW()
                        WHERE id = :id
                    """),
                    {
                        "id": config['id'],
                        "name": config['name'],
                        "prompt": prompt_template,
                        "embedding": embedding,
                        "tools": str(config.get('tools', []))
                    }
                )
                print(f"✅ Skill 更新成功")
            else:
                # 插入
                session.execute(
                    text("""
                        INSERT INTO skills (id, name, prompt_template, embedding, tool_set)
                        VALUES (:id, :name, :prompt, :embedding, :tools)
                    """),
                    {
                        "id": config['id'],
                        "name": config['name'],
                        "prompt": prompt_template,
                        "embedding": embedding,
                        "tools": str(config.get('tools', []))
                    }
                )
                print(f"✅ Skill 注册成功")

            session.commit()
            session.close()

        except Exception as e:
            print(f"❌ 注册失败: {e}")
            return

        print("\n✅ 注册完成！")

    def publish(self, skill_id: str):
        """发布 skill 到生产环境"""
        print(f"🚀 发布 skill: {skill_id}\n")

        skill_dev_dir = self.skills_dev_dir / skill_id
        skill_prod_dir = self.skills_prod_dir / skill_id

        # 检查开发目录是否存在
        if not skill_dev_dir.exists():
            print(f"❌ Skill '{skill_id}' 不存在")
            return

        # 1. 先注册到数据库
        print("📝 步骤 1/3: 注册到数据库...")
        self.register(skill_id)

        # 2. 创建数据库表（如果需要）
        print("\n📝 步骤 2/3: 创建数据库表...")
        models_path = skill_dev_dir / "models.py"
        if models_path.exists():
            try:
                from src.infrastructure.database.connection import engine, Base
                # 动态导入模型
                import importlib.util
                spec = importlib.util.spec_from_file_location("models", models_path)
                models_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(models_module)

                # 创建表
                Base.metadata.create_all(engine)
                print("✅ 数据库表创建成功")
            except Exception as e:
                print(f"⚠️  数据库表创建失败: {e}")
        else:
            print("⚠️  未找到 models.py，跳过数据库表创建")

        # 3. 复制到生产目录
        print("\n📝 步骤 3/3: 复制到生产目录...")
        if skill_prod_dir.exists():
            shutil.rmtree(skill_prod_dir)
            print(f"🗑️  删除旧版本")

        # 复制文件（排除测试文件）
        shutil.copytree(
            skill_dev_dir,
            skill_prod_dir,
            ignore=shutil.ignore_patterns('tests', '__pycache__', '*.pyc', '.DS_Store')
        )
        print(f"✅ 复制到 {skill_prod_dir}")

        print("\n🎉 发布完成！")
        print(f"\n现在可以在主系统中使用 '{skill_id}' skill 了。")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Skill 开发工具\n")
        print("用法:")
        print("  python scripts/skill_dev.py create <skill_id>   - 创建新 skill")
        print("  python scripts/skill_dev.py test <skill_id>     - 测试 skill")
        print("  python scripts/skill_dev.py register <skill_id> - 注册 skill 到数据库")
        print("  python scripts/skill_dev.py publish <skill_id>  - 发布 skill 到生产环境")
        print("\n示例:")
        print("  python scripts/skill_dev.py create writing")
        print("  python scripts/skill_dev.py test writing")
        print("  python scripts/skill_dev.py publish writing")
        return

    command = sys.argv[1]
    tool = SkillDevTool()

    if command == "create":
        if len(sys.argv) < 3:
            print("❌ 请提供 skill_id")
            return
        tool.create(sys.argv[2])

    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ 请提供 skill_id")
            return
        tool.test(sys.argv[2])

    elif command == "register":
        if len(sys.argv) < 3:
            print("❌ 请提供 skill_id")
            return
        tool.register(sys.argv[2])

    elif command == "publish":
        if len(sys.argv) < 3:
            print("❌ 请提供 skill_id")
            return
        tool.publish(sys.argv[2])

    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()
