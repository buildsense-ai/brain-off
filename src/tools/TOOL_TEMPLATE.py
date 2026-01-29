"""
工具创建模板 - 所有新工具都应该遵循这个范式

使用方法：
1. 复制这个文件
2. 重命名为 your_tool.py
3. 填写三个部分：SCHEMA, FUNCTION, VISUALIZATION
4. 在 setup.py 中注册
5. 在 registry.py 的 skill_tools 中添加映射
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================
# 第一部分：Visualization（可视化模板）
# ============================================
YOUR_TOOL_VISUALIZATION = {
    # 如果工具有多个操作类型，为每个操作定义可视化
    "operation_type_1": {
        "calling": "【正在执行操作1：{param}】",
        "success": "【✓ 操作1成功：{result}】",
        "error": "【✗ 操作1失败：{error}】"
    },
    "operation_type_2": {
        "calling": "【正在执行操作2】",
        "success": "【✓ 操作2成功】",
        "error": "【✗ 操作2失败：{error}】"
    }
}


# ============================================
# 第二部分：Schema（LLM 看到的工具定义）
# ============================================
YOUR_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "your_tool_name",  # 工具名称（必须唯一）
        "description": """工具的详细描述。

使用场景：
- 场景1：...
- 场景2：...

注意事项：
- 注意事项1
- 注意事项2
""",
        "parameters": {
            "type": "object",
            "properties": {
                # 参数定义
                "param1": {
                    "type": "string",
                    "description": "参数1的描述"
                },
                "param2": {
                    "type": "string",
                    "enum": ["option1", "option2", "option3"],
                    "description": "参数2的描述（枚举类型）"
                },
                "param3": {
                    "type": "object",
                    "description": "参数3的描述（对象类型）",
                    "properties": {
                        "nested_param": {
                            "type": "string",
                            "description": "嵌套参数"
                        }
                    }
                }
            },
            "required": ["param1"]  # 必需参数列表
        }
    }
}


# ============================================
# 第三部分：Function（实际执行的函数）
# ============================================
async def your_tool_function(
    db: AsyncSession,
    param1: str,
    param2: Optional[str] = None,
    param3: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    工具函数的实现

    Args:
        db: 数据库会话
        param1: 参数1
        param2: 参数2（可选）
        param3: 参数3（可选）

    Returns:
        执行结果字典
    """
    try:
        # 1. 参数验证
        if not param1:
            return {"error": "param1 is required"}

        # 2. 业务逻辑
        # TODO: 实现你的业务逻辑
        result = f"处理了 {param1}"

        # 3. 返回结果
        return {
            "success": True,
            "result": result,
            "param1": param1
        }

    except Exception as e:
        return {
            "error": f"执行失败: {str(e)}"
        }


# ============================================
# 注册步骤（在 setup.py 中）
# ============================================
"""
from src.tools.your_tool import (
    your_tool_function,
    YOUR_TOOL_SCHEMA,
    YOUR_TOOL_VISUALIZATION
)

def initialize_tools():
    registry = get_tool_registry()

    # 注册你的工具
    registry.register_tool(
        name="your_tool_name",
        schema=YOUR_TOOL_SCHEMA,
        function=your_tool_function,
        visualization=YOUR_TOOL_VISUALIZATION
    )
"""


# ============================================
# 技能映射步骤（在 registry.py 中）
# ============================================
"""
在 ToolRegistry.__init__() 中添加：

self.skill_tools = {
    "todo": ["database_operation", "search", "your_tool_name"],
    "writing": ["database_operation", "search"],
    "learning": ["database_operation", "search"],
    "your_skill": ["your_tool_name"]  # 或者创建新的技能领域
}
"""
