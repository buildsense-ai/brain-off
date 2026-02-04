"""
智能错误处理器

提供友好的错误消息和恢复建议
"""

from typing import Dict, List, Optional


class ErrorHandler:
    """智能错误处理器"""

    # 错误类型到建议的映射
    ERROR_SUGGESTIONS = {
        "文件不存在": {
            "reasons": [
                "文件路径错误",
                "文件未上传到工作目录",
                "文件名拼写错误"
            ],
            "actions": [
                "列出可用文件",
                "检查文件路径",
                "确认文件已上传"
            ]
        },
        "API调用失败": {
            "reasons": [
                "网络连接问题",
                "API密钥无效或过期",
                "API服务暂时不可用"
            ],
            "actions": [
                "检查网络连接",
                "验证API密钥配置",
                "稍后重试"
            ]
        },
        "需要安装": {
            "reasons": [
                "缺少必要的Python库",
                "依赖包未安装"
            ],
            "actions": [
                "运行 pip install 安装依赖",
                "检查 requirements.txt"
            ]
        },
        "转换失败": {
            "reasons": [
                "文件格式不支持",
                "文件损坏",
                "转换工具未配置"
            ],
            "actions": [
                "检查文件格式",
                "尝试使用其他文件",
                "查看错误详情"
            ]
        }
    }

    @staticmethod
    def format_error(error_msg: str, context: Optional[Dict] = None) -> str:
        """
        格式化错误消息，添加恢复建议

        Args:
            error_msg: 原始错误消息
            context: 上下文信息（可选）

        Returns:
            格式化后的错误消息
        """
        # 匹配错误类型
        matched_type = None
        for error_type in ErrorHandler.ERROR_SUGGESTIONS.keys():
            if error_type in error_msg:
                matched_type = error_type
                break

        if not matched_type:
            # 没有匹配的错误类型，返回基本格式
            return f"❌ 错误: {error_msg}"

        # 获取建议信息
        info = ErrorHandler.ERROR_SUGGESTIONS[matched_type]

        # 构建格式化消息
        formatted = f"❌ 错误: {error_msg}\n\n"
        formatted += "💡 可能的原因:\n"
        for i, reason in enumerate(info['reasons'], 1):
            formatted += f"  {i}. {reason}\n"

        formatted += "\n🔧 建议操作:\n"
        for action in info['actions']:
            formatted += f"  • {action}\n"

        formatted += "\n需要我帮你检查吗？"

        return formatted
