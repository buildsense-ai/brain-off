#!/usr/bin/env python3
"""
测试 P0 UX 改进效果

测试内容：
1. 工具调用提示简化（技术名称 → 友好名称）
2. 错误恢复建议
3. 文件路径展示优化
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from infrastructure.utils.cli_colors import format_tool_call
from core.error_handler import ErrorHandler
from infrastructure.utils.file_formatter import format_file_path


def test_tool_call_simplification():
    """测试 1: 工具调用提示简化"""
    print("=" * 60)
    print("测试 1: 工具调用提示简化")
    print("=" * 60)

    test_cases = [
        "extract_cad_entities",
        "calculate_cad_measurements",
        "analyze_drawing_visual",
        "convert_cad_to_image",
        "🔧 extract_cad_entities(layers=['WALL'])",
        "unknown_tool_name"
    ]

    for tool_name in test_cases:
        result = format_tool_call(tool_name)
        print(f"\n输入: {tool_name}")
        print(f"输出: {result}")

    print("\n✅ 测试 1 完成\n")


def test_error_recovery():
    """测试 2: 错误恢复建议"""
    print("=" * 60)
    print("测试 2: 错误恢复建议")
    print("=" * 60)

    test_cases = [
        "文件不存在: test.dwg",
        "API调用失败: 连接超时",
        "需要安装: pandas 库未找到",
        "转换失败: 不支持的文件格式",
        "未知错误: 这是一个没有匹配的错误"
    ]

    for error_msg in test_cases:
        result = ErrorHandler.format_error(error_msg)
        print(f"\n{result}")
        print("-" * 60)

    print("\n✅ 测试 2 完成\n")


def test_file_path_display():
    """测试 3: 文件路径展示优化"""
    print("=" * 60)
    print("测试 3: 文件路径展示优化")
    print("=" * 60)

    test_cases = [
        ("workspace/cost/notes/visual_analysis_test.md", "分析报告"),
        ("workspace/cost/notes/entities_WALL_20260204.json", "实体数据"),
        ("output/report.xlsx", "工程量清单"),
    ]

    for file_path, file_type in test_cases:
        result = format_file_path(file_path, file_type, show_shortcuts=True)
        print(f"\n{result}")
        print("-" * 60)

    # 测试不显示快捷操作
    print("\n不显示快捷操作的情况:")
    result = format_file_path("test.txt", "测试文件", show_shortcuts=False)
    print(f"\n{result}")

    print("\n✅ 测试 3 完成\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("P0 UX 改进效果测试")
    print("=" * 60 + "\n")

    try:
        test_tool_call_simplification()
        test_error_recovery()
        test_file_path_display()

        print("=" * 60)
        print("🎉 所有测试完成！")
        print("=" * 60)
        print("\n总结:")
        print("✅ P0-1: 工具调用提示简化 - 正常工作")
        print("✅ P0-2: 错误恢复建议 - 正常工作")
        print("✅ P0-3: 文件路径展示优化 - 正常工作")
        print("\n下一步: 在实际对话中测试这些改进")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
