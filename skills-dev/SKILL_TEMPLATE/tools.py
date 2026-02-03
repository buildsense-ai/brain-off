"""
Skill 工具实现

这里定义所有工具函数，每个函数对应一个 LLM 可调用的工具。
"""

from typing import Dict, Any, List, Optional


def example_tool(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    示例工具函数

    Args:
        param1: 参数1描述
        param2: 参数2描述（可选）

    Returns:
        Dict[str, Any]: 返回结果，包含 success 和 data/error
    """
    try:
        # 1. 参数验证
        if not param1:
            return {
                "success": False,
                "error": "param1 不能为空"
            }

        # 2. 业务逻辑
        # TODO: 实现你的工具逻辑
        result = f"处理结果: {param1}"

        # 3. 返回结果
        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# 工具注册信息（供 LLM 调用）
TOOL_DEFINITIONS = [
    {
        "name": "example_tool",
        "description": "示例工具的描述，说明它的功能和使用场景",
        "input_schema": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数1的描述"
                },
                "param2": {
                    "type": "integer",
                    "description": "参数2的描述（可选）"
                }
            },
            "required": ["param1"]
        }
    }
]
