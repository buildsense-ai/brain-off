"""
业务逻辑层

封装复杂的业务逻辑，协调 repository 和其他服务。
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ..repositories.example_repository import ExampleRepository


class ExampleService:
    """示例业务服务"""

    def __init__(self, session: Session):
        self.session = session
        self.repository = ExampleRepository(session)

    def create_item(self, name: str, description: str = None) -> Dict[str, Any]:
        """创建项目"""
        try:
            # 检查是否已存在
            existing = self.repository.find_by_name(name)
            if existing:
                return {
                    "success": False,
                    "error": f"名称 '{name}' 已存在"
                }

            # 创建新项目
            item = self.repository.create(
                name=name,
                description=description
            )

            return {
                "success": True,
                "data": item.to_dict()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_item(self, item_id: UUID) -> Dict[str, Any]:
        """获取项目"""
        item = self.repository.get_by_id(item_id)
        if not item:
            return {
                "success": False,
                "error": "项目不存在"
            }

        return {
            "success": True,
            "data": item.to_dict()
        }

    def search_items(self, keyword: str) -> Dict[str, Any]:
        """搜索项目"""
        items = self.repository.search(keyword)
        return {
            "success": True,
            "data": [item.to_dict() for item in items]
        }
