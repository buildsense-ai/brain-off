"""
工具单元测试

测试每个工具函数的功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tools import example_tool


def test_example_tool():
    """测试示例工具"""
    print("🧪 测试 example_tool...")

    # 测试正常情况
    result = example_tool("test_param")
    assert result["success"] == True
    print(f"✅ 正常情况: {result}")

    # 测试空参数
    result = example_tool("")
    assert result["success"] == False
    print(f"✅ 空参数: {result}")

    print("✅ 所有测试通过！\n")


if __name__ == "__main__":
    test_example_tool()
