"""
计划管理工具 - Agent的工作记忆系统

提供Plan & Trace能力：
- 创建和管理分析计划
- 追踪任务进度
- 记录决策过程
- 保存上下文状态
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from src.infrastructure.database.connection import get_session
from models import AnalysisPlan, PlanNote, PlanStatus, NoteType


def create_analysis_plan(
    project_name: str,
    cad_file_id: str,
    initial_tasks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    创建图纸分析计划

    Args:
        project_name: 项目名称
        cad_file_id: CAD文件ID
        initial_tasks: 初始任务列表

    Returns:
        Dict包含：
        - success: bool
        - data: {plan_id, project_name, status, tasks}
        - error: str
    """
    try:
        session = get_session()

        # 创建默认任务列表
        if not initial_tasks:
            initial_tasks = [
                "加载并分析CAD文件结构",
                "转换为图片进行视觉分析",
                "识别主要构件类型",
                "计算工程量",
                "查询定额标准",
                "生成工程量清单"
            ]

        tasks_data = {
            "pending": initial_tasks,
            "in_progress": [],
            "completed": []
        }

        # 创建计划
        plan = AnalysisPlan(
            project_name=project_name,
            cad_file_id=uuid.UUID(cad_file_id),
            status=PlanStatus.PENDING,
            tasks=tasks_data,
            context={}
        )

        session.add(plan)
        session.commit()

        return {
            "success": True,
            "data": {
                "plan_id": str(plan.id),
                "project_name": plan.project_name,
                "status": plan.status.value,
                "tasks": tasks_data
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"创建计划失败: {str(e)}"
        }


def update_plan_progress(
    plan_id: str,
    task_name: str,
    status: str,
    result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    更新计划任务进度

    Args:
        plan_id: 计划ID
        task_name: 任务名称
        status: 任务状态（pending/in_progress/completed）
        result: 任务结果（可选）

    Returns:
        Dict包含：
        - success: bool
        - data: {plan_id, updated_tasks}
        - error: str
    """
    try:
        session = get_session()
        plan = session.query(AnalysisPlan).filter_by(id=uuid.UUID(plan_id)).first()

        if not plan:
            return {
                "success": False,
                "error": f"计划不存在: {plan_id}"
            }

        tasks = plan.tasks or {"pending": [], "in_progress": [], "completed": []}

        # 从所有状态中移除该任务
        for status_key in tasks:
            if task_name in tasks[status_key]:
                tasks[status_key].remove(task_name)

        # 添加到新状态
        if status in tasks:
            tasks[status].append(task_name)

        # 更新上下文
        if result:
            context = plan.context or {}
            context[task_name] = result
            plan.context = context

        plan.tasks = tasks
        plan.updated_at = datetime.utcnow()

        # 更新计划状态
        if len(tasks["completed"]) == len(tasks["pending"]) + len(tasks["in_progress"]) + len(tasks["completed"]):
            plan.status = PlanStatus.COMPLETED

        session.commit()

        return {
            "success": True,
            "data": {
                "plan_id": str(plan.id),
                "updated_tasks": tasks
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"更新进度失败: {str(e)}"
        }


def get_plan_context(plan_id: str) -> Dict[str, Any]:
    """
    获取计划的完整上下文（Agent恢复工作状态）

    Args:
        plan_id: 计划ID

    Returns:
        Dict包含：
        - success: bool
        - data: {
            plan_id, project_name, status,
            tasks, context, notes, boq_items
          }
        - error: str
    """
    try:
        session = get_session()
        plan = session.query(AnalysisPlan).filter_by(id=uuid.UUID(plan_id)).first()

        if not plan:
            return {
                "success": False,
                "error": f"计划不存在: {plan_id}"
            }

        # 获取关联的笔记
        notes = session.query(PlanNote).filter_by(plan_id=plan.id).order_by(PlanNote.created_at).all()

        # 获取清单项
        from models import BOQItem
        boq_items = session.query(BOQItem).filter_by(plan_id=plan.id).all()

        return {
            "success": True,
            "data": {
                "plan_id": str(plan.id),
                "project_name": plan.project_name,
                "status": plan.status.value,
                "tasks": plan.tasks,
                "context": plan.context,
                "notes": [note.to_dict() for note in notes],
                "boq_items_count": len(boq_items),
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"获取上下文失败: {str(e)}"
        }


def add_plan_note(
    plan_id: str,
    note_type: str,
    content: str,
    related_entity: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    添加分析笔记（记录Agent的发现、疑问、决策）

    Args:
        plan_id: 计划ID
        note_type: 笔记类型（discovery/question/decision/calculation）
        content: 笔记内容
        related_entity: 关联的实体（CAD实体ID、清单项ID等）

    Returns:
        Dict包含：
        - success: bool
        - data: {note_id, note_type, content}
        - error: str
    """
    try:
        session = get_session()

        # 验证计划存在
        plan = session.query(AnalysisPlan).filter_by(id=uuid.UUID(plan_id)).first()
        if not plan:
            return {
                "success": False,
                "error": f"计划不存在: {plan_id}"
            }

        # 创建笔记
        note = PlanNote(
            plan_id=uuid.UUID(plan_id),
            note_type=NoteType[note_type.upper()],
            content=content,
            related_entity=related_entity
        )

        session.add(note)
        session.commit()

        return {
            "success": True,
            "data": {
                "note_id": str(note.id),
                "note_type": note.note_type.value,
                "content": note.content,
                "created_at": note.created_at.isoformat()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"添加笔记失败: {str(e)}"
        }


# 计划管理工具定义
PLAN_TOOL_DEFINITIONS = [
    {
        "name": "create_analysis_plan",
        "description": "创建图纸分析计划，初始化工作任务列表",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "项目名称"
                },
                "cad_file_id": {
                    "type": "string",
                    "description": "CAD文件ID"
                },
                "initial_tasks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "初始任务列表（可选）"
                }
            },
            "required": ["project_name", "cad_file_id"]
        }
    },
    {
        "name": "update_plan_progress",
        "description": "更新计划任务进度，标记任务状态",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "string",
                    "description": "计划ID"
                },
                "task_name": {
                    "type": "string",
                    "description": "任务名称"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                    "description": "任务状态"
                },
                "result": {
                    "type": "object",
                    "description": "任务结果（可选）"
                }
            },
            "required": ["plan_id", "task_name", "status"]
        }
    },
    {
        "name": "get_plan_context",
        "description": "获取计划的完整上下文，用于恢复工作状态",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "string",
                    "description": "计划ID"
                }
            },
            "required": ["plan_id"]
        }
    },
    {
        "name": "add_plan_note",
        "description": "添加分析笔记，记录发现、疑问或决策过程",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "string",
                    "description": "计划ID"
                },
                "note_type": {
                    "type": "string",
                    "enum": ["discovery", "question", "decision", "calculation"],
                    "description": "笔记类型"
                },
                "content": {
                    "type": "string",
                    "description": "笔记内容"
                },
                "related_entity": {
                    "type": "object",
                    "description": "关联的实体信息（可选）"
                }
            },
            "required": ["plan_id", "note_type", "content"]
        }
    }
]

