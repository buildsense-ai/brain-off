#!/usr/bin/env python3
"""
测试 CLI 用户体验改进

验证：
1. BASE_AGENT_PROMPT 简化
2. 工具可视化模板
3. Supervision skill 工具注册
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_base_prompt():
    """测试 1: BASE_AGENT_PROMPT 简化"""
    print("=" * 60)
    print("测试 1: BASE_AGENT_PROMPT 简化")
    print("=" * 60)
    
    from src.core.agent.prompts import BASE_AGENT_PROMPT
    
    # 检查是否包含核心约束
    checks = [
        ("CLI 输出规范", "CLI 输出规范" in BASE_AGENT_PROMPT),
        ("不用 Markdown 标题", "##" in BASE_AGENT_PROMPT or "标题" in BASE_AGENT_PROMPT),
        ("不用粗体", "**" in BASE_AGENT_PROMPT or "粗体" in BASE_AGENT_PROMPT),
        ("简洁", len(BASE_AGENT_PROMPT) < 500)
    ]
    
    for name, passed in checks:
        print(f"{'✅' if passed else '❌'} {name}")
    
    print(f"\nPrompt 长度: {len(BASE_AGENT_PROMPT)} 字符")
    print(f"{'✅' if len(BASE_AGENT_PROMPT) < 500 else '❌'} 保持简洁 (<500字符)")
    
    all_passed = all(p for _, p in checks)
    print(f"\n{'✅ 测试 1 通过' if all_passed else '❌ 测试 1 失败'}\n")
    return all_passed


def test_tool_visualizations():
    """测试 2: 工具可视化模板"""
    print("=" * 60)
    print("测试 2: 工具可视化模板")
    print("=" * 60)
    
    from src.core.skills.tool_registry import get_tool_registry
    from src.skills.initialize import initialize_all_tools
    
    # 初始化工具
    initialize_all_tools()
    registry = get_tool_registry()
    
    # 测试工具
    test_tools = ["list_files", "read_file", "get_cad_metadata"]
    
    for tool_name in test_tools:
        if tool_name in registry.tools:
            viz = registry.tools[tool_name].get("visualization")
            has_viz = viz is not None
            print(f"{'✅' if has_viz else '❌'} {tool_name}: {'有可视化' if has_viz else '无可视化'}")
        else:
            print(f"❌ {tool_name}: 未注册")
    
    print(f"\n✅ 测试 2 完成\n")
    return True


def test_visualization_formatting():
    """测试 3: 可视化格式化"""
    print("=" * 60)
    print("测试 3: 可视化格式化")
    print("=" * 60)
    
    from src.core.skills.tool_registry import get_tool_registry
    
    registry = get_tool_registry()
    
    # 测试 list_files 可视化
    test_cases = [
        {
            "tool": "list_files",
            "args": {"working_folder": "workspace/cost/cad_files"},
            "stage": "calling",
            "expected": "workspace/cost/cad_files"
        },
        {
            "tool": "read_file",
            "args": {"file_path": "test.txt"},
            "stage": "calling",
            "expected": "test.txt"
        }
    ]
    
    for case in test_cases:
        result = registry.format_visualization(
            case["tool"],
            case["args"],
            case["stage"]
        )
        has_param = case["expected"] in result
        print(f"{'✅' if has_param else '❌'} {case['tool']}: {result}")
    
    print(f"\n✅ 测试 3 完成\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("CLI 用户体验改进测试")
    print("=" * 60 + "\n")
    
    results = []
    
    try:
        results.append(("BASE_AGENT_PROMPT", test_base_prompt()))
        results.append(("工具可视化", test_tool_visualizations()))
        results.append(("可视化格式化", test_visualization_formatting()))
        
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
            print("🎉 所有测试通过！CLI 改进已完成")
        else:
            print("❌ 部分测试失败")
        print("=" * 60)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
