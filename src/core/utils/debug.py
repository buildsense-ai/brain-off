"""
调试模式工具

控制是否显示性能追踪和调试信息
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量读取调试模式配置
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"


def debug_print(*args, **kwargs):
    """只在调试模式下打印信息"""
    if DEBUG_MODE:
        print(*args, **kwargs)


def is_debug_mode() -> bool:
    """检查是否处于调试模式"""
    return DEBUG_MODE
