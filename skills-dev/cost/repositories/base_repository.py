"""
数据访问层基类

提供通用的 CRUD 操作。
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID


class BaseRepository:
    """基础 Repository"""

    def __init__(self, session: Session, model_class):
        self.session = session
        self.model_class = model_class

    def create(self, **kwargs) -> Any:
        """创建记录"""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get_by_id(self, id: UUID) -> Optional[Any]:
        """根据 ID 获取记录"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()

    def get_all(self, limit: int = 100) -> List[Any]:
        """获取所有记录"""
        return self.session.query(self.model_class).limit(limit).all()

    def update(self, id: UUID, **kwargs) -> Optional[Any]:
        """更新记录"""
        instance = self.get_by_id(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, id: UUID) -> bool:
        """删除记录"""
        instance = self.get_by_id(id)
        if not instance:
            return False

        self.session.delete(instance)
        self.session.commit()
        return True
