"""
性能追踪器 - 用于追踪和记录请求处理的各个步骤耗时
"""
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Step:
    """单个步骤的信息"""
    name: str
    status: str = "pending"  # pending, in_progress, completed, failed
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    error: Optional[str] = None


@dataclass
class RequestBlock:
    """单个请求的完整追踪信息"""
    request_id: str
    user_query: str
    timestamp: str
    status: str = "processing"  # processing, completed, failed
    sync_steps: List[Step] = field(default_factory=list)
    async_steps: List[Step] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    response: Optional[str] = None
    error: Optional[str] = None
    # 上下文内容
    context_content: Optional[Dict[str, Any]] = None


class PerformanceTracker:
    """性能追踪器"""

    # 全局存储所有请求的追踪信息
    _all_requests: List[RequestBlock] = []
    _max_history = 100  # 最多保存 100 条历史记录

    def __init__(self, user_query: str, request_id: Optional[str] = None):
        """
        初始化追踪器

        Args:
            user_query: 用户查询
            request_id: 请求 ID（可选）
        """
        self.request_id = request_id or str(uuid4())[:8]
        self.user_query = user_query
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.block = RequestBlock(
            request_id=self.request_id,
            user_query=user_query,
            timestamp=self.timestamp
        )

        # 当前正在执行的步骤
        self._current_sync_step: Optional[Step] = None
        self._current_async_steps: Dict[str, Step] = {}

    def start_sync_step(self, name: str):
        """开始一个同步步骤"""
        step = Step(name=name, status="in_progress", start_time=time.time())
        self.block.sync_steps.append(step)
        self._current_sync_step = step
        print(f"⏱️  [{self.request_id}] 开始: {name}")

    def end_sync_step(self, name: str, error: Optional[str] = None):
        """结束一个同步步骤"""
        for step in self.block.sync_steps:
            if step.name == name and step.status == "in_progress":
                step.end_time = time.time()
                step.duration = step.end_time - step.start_time
                step.status = "failed" if error else "completed"
                step.error = error

                status_icon = "❌" if error else "✅"
                print(f"{status_icon} [{self.request_id}] {name}: {step.duration:.2f}s")
                break

    def start_async_step(self, name: str):
        """开始一个异步步骤"""
        step = Step(name=name, status="in_progress", start_time=time.time())
        self.block.async_steps.append(step)
        self._current_async_steps[name] = step
        print(f"⏱️  [{self.request_id}] 异步开始: {name}")

    def end_async_step(self, name: str, error: Optional[str] = None):
        """结束一个异步步骤"""
        for step in self.block.async_steps:
            if step.name == name and step.status == "in_progress":
                step.end_time = time.time()
                step.duration = step.end_time - step.start_time
                step.status = "failed" if error else "completed"
                step.error = error

                status_icon = "❌" if error else "✅"
                print(f"{status_icon} [{self.request_id}] 异步完成: {name}: {step.duration:.2f}s")

                if name in self._current_async_steps:
                    del self._current_async_steps[name]
                break

    def get_progress(self) -> tuple[float, str]:
        """
        计算当前进度

        Returns:
            (progress, description): 进度值 (0.0-1.0) 和描述文本
        """
        try:
            total_steps = len(self.block.sync_steps)
            if total_steps == 0:
                return 0.0, "🔄 初始化..."

            completed_steps = sum(1 for s in self.block.sync_steps if s.status == "completed")
            progress = completed_steps / total_steps

            # 找到当前正在执行的步骤
            current_step = None
            for step in self.block.sync_steps:
                if step.status == "in_progress":
                    current_step = step
                    break

            if current_step:
                desc = f"⏳ {current_step.name}..."
            elif completed_steps == total_steps:
                desc = "✅ 完成"
            else:
                desc = f"🔄 处理中 ({completed_steps}/{total_steps})"

            return progress, desc
        except Exception as e:
            print(f"❌ get_progress error: {e}")
            print(f"   sync_steps: {self.block.sync_steps}")
            return 0.0, "🔄 处理中..."

    def set_context_content(self, context_content: Dict[str, Any]):
        """设置上下文内容"""
        self.block.context_content = context_content

    def complete(self, response: Optional[str] = None, error: Optional[str] = None):
        """完成整个请求的追踪"""
        self.block.end_time = time.time()
        self.block.total_duration = self.block.end_time - self.block.start_time
        self.block.status = "failed" if error else "completed"
        self.block.response = response
        self.block.error = error

        # 保存到全局历史
        PerformanceTracker._all_requests.append(self.block)
        if len(PerformanceTracker._all_requests) > PerformanceTracker._max_history:
            PerformanceTracker._all_requests.pop(0)

        # 打印总结
        status_icon = "❌" if error else "✅"
        print(f"\n{status_icon} [{self.request_id}] 请求完成")
        print(f"📊 总耗时: {self.block.total_duration:.2f}s")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    def get_summary(self) -> Dict[str, Any]:
        """获取当前请求的摘要"""
        return {
            "request_id": self.request_id,
            "user_query": self.user_query,
            "timestamp": self.timestamp,
            "status": self.block.status,
            "sync_steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "duration": s.duration,
                    "error": s.error
                }
                for s in self.block.sync_steps
            ],
            "async_steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "duration": s.duration,
                    "error": s.error
                }
                for s in self.block.async_steps
            ],
            "total_duration": self.block.total_duration,
            "response": self.block.response[:100] + "..." if self.block.response and len(self.block.response) > 100 else self.block.response
        }

    @classmethod
    def get_all_requests(cls) -> List[RequestBlock]:
        """获取所有历史请求"""
        return cls._all_requests

    @classmethod
    def get_active_requests(cls) -> List[RequestBlock]:
        """获取正在进行的请求"""
        return [req for req in cls._all_requests if req.status == "processing"]

    @classmethod
    def get_recent_requests(cls, limit: int = 10) -> List[RequestBlock]:
        """获取最近的 N 个请求"""
        return cls._all_requests[-limit:]

    @classmethod
    def clear_history(cls):
        """清除历史记录"""
        cls._all_requests.clear()
        print("🗑️  性能追踪历史已清除")
