"""
Writing Skill 工具实现

提供文档创建和管理功能。
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


# 简单的内存存储（实际项目中应该使用数据库）
DOCUMENTS = {}


def create_document(title: str, content: str) -> Dict[str, Any]:
    """
    创建新文档

    Args:
        title: 文档标题
        content: 文档内容

    Returns:
        Dict[str, Any]: 返回结果
    """
    try:
        if not title:
            return {
                "success": False,
                "error": "标题不能为空"
            }

        if not content:
            return {
                "success": False,
                "error": "内容不能为空"
            }

        doc_id = str(uuid.uuid4())
        document = {
            "id": doc_id,
            "title": title,
            "content": content,
            "created_at": datetime.now().isoformat()
        }

        DOCUMENTS[doc_id] = document

        return {
            "success": True,
            "data": {
                "id": doc_id,
                "title": title,
                "message": f"文档 '{title}' 创建成功"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def list_documents() -> Dict[str, Any]:
    """
    列出所有文档

    Returns:
        Dict[str, Any]: 返回结果
    """
    try:
        docs = [
            {
                "id": doc["id"],
                "title": doc["title"],
                "created_at": doc["created_at"]
            }
            for doc in DOCUMENTS.values()
        ]

        return {
            "success": True,
            "data": {
                "documents": docs,
                "count": len(docs)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_document(doc_id: str) -> Dict[str, Any]:
    """
    获取文档内容

    Args:
        doc_id: 文档 ID

    Returns:
        Dict[str, Any]: 返回结果
    """
    try:
        if doc_id not in DOCUMENTS:
            return {
                "success": False,
                "error": f"文档 {doc_id} 不存在"
            }

        return {
            "success": True,
            "data": DOCUMENTS[doc_id]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# 工具注册信息（供 LLM 调用）
TOOL_DEFINITIONS = [
    {
        "name": "create_document",
        "description": "创建新文档",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "文档标题"
                },
                "content": {
                    "type": "string",
                    "description": "文档内容"
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "list_documents",
        "description": "列出所有文档",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_document",
        "description": "获取指定文档的内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "文档 ID"
                }
            },
            "required": ["doc_id"]
        }
    }
]
