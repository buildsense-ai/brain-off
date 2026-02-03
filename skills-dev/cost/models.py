"""
工程造价 Skill 数据模型

包含5个核心表：
1. CADFile - CAD文件管理
2. AnalysisPlan - 分析计划（工作记忆）
3. PlanNote - 分析笔记（追踪决策）
4. BOQItem - 清单项目（Bill of Quantities）
5. VisualAnalysis - 视觉分析结果缓存
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.infrastructure.database.connection import Base


class FileType(enum.Enum):
    """CAD文件类型"""
    DXF = "dxf"
    DWG = "dwg"
    PDF = "pdf"


class PlanStatus(enum.Enum):
    """分析计划状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class NoteType(enum.Enum):
    """笔记类型"""
    DISCOVERY = "discovery"  # 发现
    QUESTION = "question"    # 疑问
    DECISION = "decision"    # 决策
    CALCULATION = "calculation"  # 计算过程


class CADFile(Base):
    """CAD文件表"""
    __tablename__ = "cost_cad_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(500), nullable=False, comment="原始文件名")
    file_path = Column(String(1000), nullable=False, comment="存储路径")
    file_type = Column(Enum(FileType), nullable=False, comment="文件类型")
    file_size = Column(Integer, comment="文件大小(字节)")

    # CAD元数据
    metadata = Column(JSONB, comment="CAD元数据：图层、比例、单位等")

    # 关联关系
    analysis_plans = relationship("AnalysisPlan", back_populates="cad_file")
    visual_analyses = relationship("VisualAnalysis", back_populates="cad_file")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type.value if self.file_type else None,
            "file_size": self.file_size,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AnalysisPlan(Base):
    """分析计划表 - Agent的工作记忆"""
    __tablename__ = "cost_analysis_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(500), nullable=False, comment="项目名称")
    cad_file_id = Column(UUID(as_uuid=True), ForeignKey("cost_cad_files.id"), comment="关联CAD文件")

    status = Column(Enum(PlanStatus), default=PlanStatus.PENDING, comment="计划状态")

    # 工作上下文（Agent可反复访问）
    tasks = Column(JSONB, comment="任务列表：待办、进行中、已完成")
    context = Column(JSONB, comment="分析上下文：已识别的构件、计算结果等")

    # 关联关系
    cad_file = relationship("CADFile", back_populates="analysis_plans")
    notes = relationship("PlanNote", back_populates="plan", cascade="all, delete-orphan")
    boq_items = relationship("BOQItem", back_populates="plan", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "project_name": self.project_name,
            "cad_file_id": str(self.cad_file_id) if self.cad_file_id else None,
            "status": self.status.value if self.status else None,
            "tasks": self.tasks,
            "context": self.context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PlanNote(Base):
    """分析笔记表 - 追踪Agent的决策过程"""
    __tablename__ = "cost_plan_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("cost_analysis_plans.id"), nullable=False)

    note_type = Column(Enum(NoteType), nullable=False, comment="笔记类型")
    content = Column(Text, nullable=False, comment="笔记内容")
    related_entity = Column(JSONB, comment="关联的CAD实体或清单项")

    # 关联关系
    plan = relationship("AnalysisPlan", back_populates="notes")

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "plan_id": str(self.plan_id),
            "note_type": self.note_type.value if self.note_type else None,
            "content": self.content,
            "related_entity": self.related_entity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BOQItem(Base):
    """工程量清单项目表 (Bill of Quantities)"""
    __tablename__ = "cost_boq_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("cost_analysis_plans.id"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("cost_boq_items.id"), comment="父项目ID（用于子清单）")

    # 清单基本信息
    code = Column(String(100), comment="项目编码（如：04-01-001）")
    name = Column(String(500), nullable=False, comment="项目名称")
    unit = Column(String(50), comment="计量单位（如：m²、m³、m）")

    # 工程量和价格
    quantity = Column(Float, comment="工程量")
    unit_price = Column(Float, comment="单价")
    total_price = Column(Float, comment="合价")

    # 溯源信息
    source = Column(JSONB, comment="来源：CAD实体ID、计算规则、定额依据")
    metadata = Column(JSONB, comment="附加信息：材料规格、施工说明等")

    # 关联关系
    plan = relationship("AnalysisPlan", back_populates="boq_items")
    children = relationship("BOQItem", backref="parent", remote_side=[id])

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "plan_id": str(self.plan_id),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "code": self.code,
            "name": self.name,
            "unit": self.unit,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class VisualAnalysis(Base):
    """视觉分析结果缓存表"""
    __tablename__ = "cost_visual_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cad_file_id = Column(UUID(as_uuid=True), ForeignKey("cost_cad_files.id"), nullable=False)

    image_path = Column(String(1000), comment="生成的图片路径")
    analysis_type = Column(String(100), comment="分析类型：ocr/symbol/legend")
    analysis_result = Column(JSONB, comment="分析结果：识别的文字、符号等")

    # 关联关系
    cad_file = relationship("CADFile", back_populates="visual_analyses")

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "cad_file_id": str(self.cad_file_id),
            "image_path": self.image_path,
            "analysis_type": self.analysis_type,
            "analysis_result": self.analysis_result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
