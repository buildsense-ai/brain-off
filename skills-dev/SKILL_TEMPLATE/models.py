"""
数据模型定义

如果你的 skill 需要数据库表，在这里定义 SQLAlchemy 模型。
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from src.infrastructure.database.connection import Base


class ExampleModel(Base):
    """示例数据模型"""
    __tablename__ = "example_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
