"""
文件路径格式化工具

提供友好的文件路径展示和快捷操作提示
"""

from pathlib import Path
from typing import Optional


def format_file_path(
    file_path: str,
    file_type: str = "文件",
    show_shortcuts: bool = True
) -> str:
    """
    格式化文件路径输出，添加快捷操作提示

    Args:
        file_path: 文件路径（相对或绝对）
        file_type: 文件类型描述（如 "分析报告"、"实体数据"）
        show_shortcuts: 是否显示快捷操作提示

    Returns:
        格式化后的文件路径信息
    """
    try:
        path_obj = Path(file_path)
        abs_path = path_obj.absolute()
        rel_path = file_path

        # 基本信息
        output = f"📄 {file_type}已保存:\n"
        output += f"   {rel_path}\n"

        if show_shortcuts:
            output += "\n💡 快捷操作:\n"
            output += f"   • 查看内容: read_file(\"{rel_path}\")\n"
            output += f"   • 打开文件: open {abs_path}\n"

        return output

    except Exception as e:
        return f"📄 {file_type}已保存: {file_path}"
