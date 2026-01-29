"""
任务管理工具 - database_operation

从 tools_simplified.py 提取
"""
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.task_repository import TaskRepository
from src.repositories.tag_repository import TagRepository
from src.services.embedding_service import get_embedding_service


# Visualization templates
DATABASE_OPERATION_VISUALIZATION = {
    "create_task": {
        "calling": "【创建任务卡：\"{title}\"】",
        "success": "【✓ 任务已创建】",
        "error": "【✗ 创建失败：{error}】"
    },
    "update_task": {
        "calling": "【更新任务】",
        "success": "【✓ 已更新：\"{title}\"】",
        "error": "【✗ 更新失败：{error}】"
    },
    "delete_task": {
        "calling": "【删除任务】",
        "success": "【✓ 已删除：\"{title}\"】",
        "error": "【✗ 删除失败：{error}】"
    }
}


# Tool Schema
DATABASE_OPERATION_SCHEMA = {
    "type": "function",
    "function": {
        "name": "database_operation",
        "description": """统一的数据库操作工具。支持任务的创建、更新、删除等操作。

使用场景：
- 捕获想法：创建 status=brainstorm 的任务
- 创建任务：创建 status=inbox 的任务
- 更新任务：修改任务状态、优先级、标签等
- 删除任务：软删除任务
- 管理标签：创建或获取标签""",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["create_task", "update_task", "delete_task"],
                    "description": "操作类型"
                },
                "task_data": {
                    "type": "object",
                    "description": "任务数据（用于 create_task 和 update_task）",
                    "properties": {
                        "task_id": {"type": "string", "description": "任务 ID（更新时必需）"},
                        "title": {"type": "string", "description": "任务标题"},
                        "description": {"type": "string", "description": "任务描述"},
                        "status": {
                            "type": "string",
                            "enum": ["brainstorm", "inbox", "active", "waiting", "someday", "completed", "archived"],
                            "description": "任务状态"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["urgent", "high", "medium", "low", "none"],
                            "description": "优先级"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表"
                        },
                        "energy_level": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "所需精力"
                        },
                        "estimated_duration": {
                            "type": "integer",
                            "description": "预计耗时（分钟）"
                        }
                    }
                }
            },
            "required": ["operation"]
        }
    }
}


async def database_operation_tool(
    db: AsyncSession,
    operation: str,
    task_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    执行数据库操作

    Args:
        db: 数据库会话
        operation: 操作类型
        task_data: 任务数据

    Returns:
        操作结果
    """
    task_repo = TaskRepository(db)
    tag_repo = TagRepository(db)
    embedding_service = get_embedding_service()

    try:
        if operation == "create_task":
            if not task_data or "title" not in task_data:
                return {"error": "title is required for create_task"}

            # 生成 embedding
            content = f"{task_data['title']}\n{task_data.get('description', '')}"
            embedding = await embedding_service.generate(content)

            # 创建任务
            task = await task_repo.create(
                title=task_data["title"],
                description=task_data.get("description"),
                status=task_data.get("status", "brainstorm"),
                priority=task_data.get("priority"),
                energy_level=task_data.get("energy_level"),
                estimated_duration=task_data.get("estimated_duration"),
                embedding=embedding
            )

            # 添加标签
            if task_data.get("tags"):
                for tag_name in task_data["tags"]:
                    tag = await tag_repo.get_or_create(tag_name)
                    await task_repo.add_tag(task.id, tag.id)

            return {
                "task_id": str(task.id),
                "title": task.title,
                "status": task.status,
                "created_at": task.created_at.isoformat()
            }

        elif operation == "update_task":
            if not task_data or "task_id" not in task_data:
                return {"error": "task_id is required for update_task"}

            task_id = UUID(task_data["task_id"])
            task = await task_repo.get_by_id(task_id)

            if not task:
                return {"error": f"Task {task_id} not found"}

            # 更新字段
            update_data = {}
            for field in ["title", "description", "status", "priority", "energy_level", "estimated_duration"]:
                if field in task_data:
                    update_data[field] = task_data[field]

            # 如果标题或描述改变，重新生成 embedding
            if "title" in update_data or "description" in update_data:
                content = f"{update_data.get('title', task.title)}\n{update_data.get('description', task.description or '')}"
                update_data["embedding"] = await embedding_service.generate(content)

            updated_task = await task_repo.update(task_id, **update_data)

            # 更新标签
            if "tags" in task_data:
                await task_repo.remove_all_tags(task_id)
                for tag_name in task_data["tags"]:
                    tag = await tag_repo.get_or_create(tag_name)
                    await task_repo.add_tag(task_id, tag.id)

            return {
                "task_id": str(updated_task.id),
                "title": updated_task.title,
                "status": updated_task.status,
                "updated_at": updated_task.updated_at.isoformat()
            }

        elif operation == "delete_task":
            if not task_data or "task_id" not in task_data:
                return {"error": "task_id is required for delete_task"}

            task_id = UUID(task_data["task_id"])
            task = await task_repo.get_by_id(task_id)

            if not task:
                return {"error": f"Task {task_id} not found"}

            task_title = task.title
            await task_repo.soft_delete(task_id)

            return {
                "task_id": str(task_id),
                "title": task_title,
                "deleted": True
            }

        else:
            return {"error": f"Unknown operation: {operation}"}

    except Exception as e:
        return {"error": f"Operation failed: {str(e)}"}
