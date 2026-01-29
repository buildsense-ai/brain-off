"""
测试工具注册表

运行方式：
PYTHONPATH=/Users/zhuhanyuan/Documents/chatbot python scripts/test_tool_registry.py
"""
import asyncio
from src.tools.setup import initialize_tools


async def test_tool_registry():
    """测试工具注册表"""
    print("=== 测试工具注册表 ===\n")

    # 初始化工具
    registry = initialize_tools()

    # 1. 测试获取所有工具
    print("1. 获取所有工具 schemas:")
    all_schemas = registry.get_tool_schemas()
    print(f"   总共 {len(all_schemas)} 个工具")
    for schema in all_schemas:
        tool_name = schema["function"]["name"]
        print(f"   - {tool_name}")

    # 2. 测试获取特定技能的工具
    print("\n2. 获取 'todo' 技能的工具:")
    todo_schemas = registry.get_tool_schemas(skill_domain="todo")
    print(f"   总共 {len(todo_schemas)} 个工具")
    for schema in todo_schemas:
        tool_name = schema["function"]["name"]
        print(f"   - {tool_name}")

    # 3. 测试可视化格式化
    print("\n3. 测试可视化格式化:")
    viz_text = registry.format_visualization(
        tool_name="database_operation",
        arguments={
            "operation": "create_task",
            "task_data": {"title": "测试任务"}
        },
        stage="calling"
    )
    print(f"   {viz_text}")

    print("\n✅ 工具注册表测试完成！")


if __name__ == "__main__":
    asyncio.run(test_tool_registry())
