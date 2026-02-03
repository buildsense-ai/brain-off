"""
Todo Skill 工具初始化
"""
from src.core.skills.tool_registry import get_tool_registry
from src.skills.todo.tools import (
    database_operation_tool,
    DATABASE_OPERATION_SCHEMA,
    DATABASE_OPERATION_VISUALIZATION
)
from src.skills.todo.search_tools import (
    search_tool,
    SEARCH_SCHEMA,
    SEARCH_VISUALIZATION
)


def initialize_todo_tools():
    """初始化 Todo Skill 的工具"""
    registry = get_tool_registry()

    # 注册任务管理工具
    registry.register_tool(
        name="database_operation",
        schema=DATABASE_OPERATION_SCHEMA,
        function=database_operation_tool,
        visualization=DATABASE_OPERATION_VISUALIZATION
    )

    # 注册搜索工具
    registry.register_tool(
        name="search",
        schema=SEARCH_SCHEMA,
        function=search_tool,
        visualization=SEARCH_VISUALIZATION
    )

    return registry
