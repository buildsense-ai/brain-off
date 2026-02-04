#!/usr/bin/env python3
"""
测试 supervision skill 配置

验证内容：
1. skill 目录结构
2. config.json 配置
3. skill.md 提示词
4. tools.py 工具定义
5. workspace 目录
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_directory_structure():
    """测试 1: 目录结构"""
    print("=" * 60)
    print("测试 1: 目录结构")
    print("=" * 60)
    
    required_dirs = [
        "skills/supervision",
        "skills-dev/supervision",
        "workspace/supervision",
        "workspace/supervision/cad_files",
        "workspace/supervision/rendered",
        "workspace/supervision/notes",
        "workspace/supervision/projects"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {dir_path}")
        if not exists:
            all_exist = False
    
    print(f"\n{'✅ 测试 1 通过' if all_exist else '❌ 测试 1 失败'}\n")
    return all_exist

def test_config_json():
    """测试 2: config.json 配置"""
    print("=" * 60)
    print("测试 2: config.json 配置")
    print("=" * 60)
    
    config_path = project_root / "skills/supervision/config.json"
    
    if not config_path.exists():
        print("❌ config.json 不存在")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必要字段
        required_fields = {
            "id": "supervision",
            "name": "工程监理审核",
            "version": "1.0.0"
        }
        
        all_valid = True
        for field, expected in required_fields.items():
            actual = config.get(field)
            match = actual == expected
            status = "✅" if match else "❌"
            print(f"{status} {field}: {actual}")
            if not match:
                all_valid = False
        
        # 检查工具列表
        tools = config.get("tools", [])
        print(f"\n工具数量: {len(tools)}")
        print(f"工具列表: {', '.join(tools[:3])}...")
        
        # 检查 workspace 配置
        workspace = config.get("workspace", {})
        working_dir = workspace.get("working_directory")
        print(f"\n工作目录: {working_dir}")
        
        if working_dir != "workspace/supervision":
            print("❌ 工作目录配置错误")
            all_valid = False
        
        print(f"\n{'✅ 测试 2 通过' if all_valid else '❌ 测试 2 失败'}\n")
        return all_valid
        
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return False

def test_skill_md():
    """测试 3: skill.md 提示词"""
    print("=" * 60)
    print("测试 3: skill.md 提示词")
    print("=" * 60)
    
    skill_md_path = project_root / "skills/supervision/skill.md"
    
    if not skill_md_path.exists():
        print("❌ skill.md 不存在")
        return False
    
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键词
        keywords = [
            "工程监理审核助手",
            "workspace/supervision",
            "合规性检查",
            "合理化建议",
            "监理审核重点"
        ]
        
        all_found = True
        for keyword in keywords:
            found = keyword in content
            status = "✅" if found else "❌"
            print(f"{status} 包含关键词: {keyword}")
            if not found:
                all_found = False
        
        print(f"\n文件大小: {len(content)} 字符")
        print(f"\n{'✅ 测试 3 通过' if all_found else '❌ 测试 3 失败'}\n")
        return all_found
        
    except Exception as e:
        print(f"❌ 读取 skill.md 失败: {e}")
        return False

def test_tools_py():
    """测试 4: tools.py 工具定义"""
    print("=" * 60)
    print("测试 4: tools.py 工具定义")
    print("=" * 60)
    
    tools_path = project_root / "skills-dev/supervision/tools.py"
    
    if not tools_path.exists():
        print("❌ tools.py 不存在")
        return False
    
    try:
        with open(tools_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查路径是否正确修改
        has_cost_path = "workspace/cost" in content
        has_supervision_path = "workspace/supervision" in content
        
        print(f"{'❌' if has_cost_path else '✅'} 不包含 workspace/cost 路径")
        print(f"{'✅' if has_supervision_path else '❌'} 包含 workspace/supervision 路径")
        
        # 检查工具函数
        tool_functions = [
            "get_cad_metadata",
            "get_cad_regions",
            "render_cad_region",
            "extract_cad_entities",
            "convert_dwg_to_dxf"
        ]
        
        all_found = True
        for func in tool_functions:
            found = f"def {func}" in content
            status = "✅" if found else "❌"
            print(f"{status} 工具函数: {func}")
            if not found:
                all_found = False
        
        success = not has_cost_path and has_supervision_path and all_found
        print(f"\n{'✅ 测试 4 通过' if success else '❌ 测试 4 失败'}\n")
        return success
        
    except Exception as e:
        print(f"❌ 读取 tools.py 失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Supervision Skill 配置测试")
    print("=" * 60 + "\n")
    
    results = []
    
    try:
        results.append(("目录结构", test_directory_structure()))
        results.append(("config.json", test_config_json()))
        results.append(("skill.md", test_skill_md()))
        results.append(("tools.py", test_tools_py()))
        
        # 总结
        print("=" * 60)
        print("测试总结")
        print("=" * 60)
        
        for name, passed in results:
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{status} - {name}")
        
        all_passed = all(r[1] for r in results)
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 所有测试通过！supervision skill 配置成功")
            print("\n下一步:")
            print("  python chat.py --skill supervision")
        else:
            print("❌ 部分测试失败，请检查配置")
        print("=" * 60)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
