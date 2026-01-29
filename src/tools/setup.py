"""
工具初始化 - 注册所有工具到注册表
"""
from src.tools.registry import get_tool_registry
from src.tools.todo_tools import (
    database_operation_tool,
    DATABASE_OPERATION_SCHEMA,
    DATABASE_OPERATION_VISUALIZATION
)
from src.tools.search_tools import (
    search_tool,
    SEARCH_SCHEMA,
    SEARCH_VISUALIZATION
)


def initialize_tools():
    """初始化并注册所有工具"""
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
