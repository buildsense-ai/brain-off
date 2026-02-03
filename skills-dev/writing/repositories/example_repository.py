"""
示例 Repository

继承 BaseRepository，添加特定的查询方法。
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from ..models import ExampleModel


class ExampleRepository(BaseRepository):
    """示例数据访问层"""

    def __init__(self, session: Session):
        super().__init__(session, ExampleModel)

    def find_by_name(self, name: str) -> Optional[ExampleModel]:
        """根据名称查找"""
        return self.session.query(ExampleModel).filter(
            ExampleModel.name == name
        ).first()

    def search(self, keyword: str, limit: int = 10) -> List[ExampleModel]:
        """搜索"""
        return self.session.query(ExampleModel).filter(
            ExampleModel.name.ilike(f"%{keyword}%")
        ).limit(limit).all()
