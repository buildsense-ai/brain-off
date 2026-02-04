"""
测试实际 agent 中的工具定义格式
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.skills.tool_registry import get_tool_registry

# 获取工具注册表
registry = get_tool_registry()

print("="*60)
print("工具注册表状态")
print("="*60)
print(f"已注册工具数量: {len(registry.tools)}")
print(f"已注册工具列表: {list(registry.tools.keys())}")

# 获取 cost skill 的工具
cost_tools = registry.get_tools_by_names([
    "list_files",
    "read_file",
    "write_file"
])

print("\n" + "="*60)
print("Cost Skill 工具定义")
print("="*60)
print(f"请求的工具: ['list_files', 'read_file', 'write_file']")
print(f"返回的工具数量: {len(cost_tools)}")

for i, tool in enumerate(cost_tools, 1):
    print(f"\n[工具 {i}]")
    print(f"类型: {tool.get('type')}")
    print(f"名称: {tool.get('function', {}).get('name')}")

if cost_tools:
    print("\n" + "="*60)
    print("完整的第一个工具定义:")
    print("="*60)
    import json
    print(json.dumps(cost_tools[0], indent=2, ensure_ascii=False))
else:
    print("\n❌ 没有找到任何工具！工具未注册。")

