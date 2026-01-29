"""
工具注册表 - 统一管理所有工具

功能：
1. 注册工具（schema + function）
2. 根据技能领域获取工具
3. 执行工具调用
4. 格式化工具可视化
"""
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.ext.asyncio import AsyncSession


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        # 工具存储: {tool_name: {schema, function, visualization}}
        self.tools: Dict[str, Dict[str, Any]] = {}

        # 技能领域到工具的映射
        self.skill_tools: Dict[str, List[str]] = {
            "todo": ["database_operation", "search"],
            "writing": ["database_operation", "search"],
            "learning": ["database_operation", "search"],
        }

    def register_tool(
        self,
        name: str,
        schema: Dict[str, Any],
        function: Callable,
        visualization: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        注册工具

        Args:
            name: 工具名称
            schema: 工具 schema（用于 LLM function calling）
            function: 工具函数
            visualization: 可视化模板（可选）
        """
        self.tools[name] = {
            "schema": schema,
            "function": function,
            "visualization": visualization or {}
        }

    def get_tool_schemas(self, skill_domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取工具 schemas

        Args:
            skill_domain: 技能领域（如果指定，只返回该领域的工具）

        Returns:
            工具 schema 列表
        """
        if skill_domain and skill_domain in self.skill_tools:
            tool_names = self.skill_tools[skill_domain]
            return [
                self.tools[name]["schema"]
                for name in tool_names
                if name in self.tools
            ]

        # 返回所有工具
        return [tool["schema"] for tool in self.tools.values()]

    async def execute_tool(
        self,
        tool_name: str,
        db: AsyncSession,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行工具

        Args:
            tool_name: 工具名称
            db: 数据库会话
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        tool_function = self.tools[tool_name]["function"]

        try:
            result = await tool_function(db, **kwargs)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def format_visualization(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        stage: str = "calling"
    ) -> str:
        """
        格式化工具可视化文本

        Args:
            tool_name: 工具名称
            arguments: 工具参数
            stage: 阶段（calling, success, error）

        Returns:
            格式化后的可视化文本
        """
        if tool_name not in self.tools:
            return f"[调用工具: {tool_name}]"

        visualization = self.tools[tool_name].get("visualization")
        if not visualization:
            return f"[调用工具: {tool_name}]"

        # 对于 database_operation，获取操作特定的模板
        if tool_name == "database_operation":
            operation = arguments.get("operation", "")
            op_viz = visualization.get(operation, {})
            template = op_viz.get(stage, "")

            if not template:
                return f"[{operation}]"

            # 提取数据用于格式化
            task_data = arguments.get("task_data", {})
            title = arguments.get("title", task_data.get("title", ""))

            try:
                return template.format(
                    title=title,
                    error=arguments.get("error", "")
                )
            except KeyError:
                return template

        # 对于 search 工具
        elif tool_name == "search":
            template = visualization.get(stage, "")
            if not template:
                return "[搜索]"

            try:
                return template.format(
                    query=arguments.get("query", ""),
                    count=arguments.get("count", 0),
                    error=arguments.get("error", "")
                )
            except KeyError:
                return template

        return f"[调用工具: {tool_name}]"


# 全局工具注册表实例
_tool_registry = None


def get_tool_registry() -> ToolRegistry:
    """获取全局工具注册表实例"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry
