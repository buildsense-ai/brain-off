"""
工具单元测试

测试每个工具函数的功能。
"""

import sys
from pathlib import Path

# 添加 skill 目录到 Python 路径
skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(skill_dir))

from tools import create_document, list_documents, get_document


def test_create_document():
    """测试创建文档"""
    print("🧪 测试 create_document...")

    # 测试正常情况
    result = create_document("测试文档", "这是测试内容")
    assert result["success"] == True
    print(f"✅ 创建成功: {result['data']['message']}")

    # 测试空标题
    result = create_document("", "内容")
    assert result["success"] == False
    print(f"✅ 空标题验证: {result['error']}")

    print()


def test_list_documents():
    """测试列出文档"""
    print("🧪 测试 list_documents...")

    result = list_documents()
    assert result["success"] == True
    print(f"✅ 文档数量: {result['data']['count']}")
    print()


if __name__ == "__main__":
    test_create_document()
    test_list_documents()
    print("✅ 所有测试通过！")
