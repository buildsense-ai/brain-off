#!/usr/bin/env python3
"""测试工具可视化修复"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.skills.tool_registry import get_tool_registry
from src.skills.initialize import initialize_all_tools

def test_list_files_visualization():
    """测试 list_files 可视化"""
    print("=" * 60)
    print("测试 list_files 可视化修复")
    print("=" * 60)
    
    # 初始化工具
    initialize_all_tools()
    registry = get_tool_registry()
    
    # 测试 calling 阶段
    calling_viz = registry.format_visualization(
        "list_files",
        {"working_folder": "workspace/cost/cad_files"},
        "calling"
    )
    print(f"\nCalling 阶段:")
    print(f"  {calling_viz}")
    has_folder = "workspace/cost/cad_files" in calling_viz
    print(f"  {'✅' if has_folder else '❌'} 包含目录路径")
    
    # 测试 success 阶段
    success_viz = registry.format_visualization(
        "list_files",
        {
            "working_folder": "workspace/cost/cad_files",
            "file_count": 15,
            "directory_count": 3
        },
        "success"
    )
    print(f"\nSuccess 阶段:")
    print(f"  {success_viz}")
    has_count = "15" in success_viz
    no_placeholder = "{file_count}" not in success_viz
    print(f"  {'✅' if has_count else '❌'} 显示文件数量")
    print(f"  {'✅' if no_placeholder else '❌'} 没有占位符")
    
    return has_folder and has_count and no_placeholder

if __name__ == "__main__":
    result = test_list_files_visualization()
    print(f"\n{'✅ 测试通过' if result else '❌ 测试失败'}")
    sys.exit(0 if result else 1)
