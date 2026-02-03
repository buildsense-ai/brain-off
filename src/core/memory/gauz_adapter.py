"""
GauzMem 适配器 - 冗余挂载到现有记忆系统

功能：
1. 调用 GauzMem API 召回记忆
2. 存储对话到 GauzMem
3. 不影响现有的本地记忆系统
"""
from typing import List, Dict, Any, Optional
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 加载 GauzMem 独立配置文件
gauz_env_path = Path(__file__).parent.parent.parent.parent / ".env.gauz"
if gauz_env_path.exists():
    load_dotenv(gauz_env_path)

# 尝试导入 GauzMem 客户端
try:
    # 添加 gauz-memory-client 到路径
    gauz_client_path = Path(__file__).parent.parent.parent.parent.parent / "GauzMem" / "gauz-memory-client"
    if gauz_client_path.exists():
        sys.path.insert(0, str(gauz_client_path))

    from gauz_memory_client import GauzMemoryClient, GauzMemoryConfig, GauzMemoryError
    GAUZ_AVAILABLE = True
except ImportError:
    GAUZ_AVAILABLE = False
    print("⚠️ GauzMem 客户端未安装，将跳过 GauzMem 集成")


class GauzMemAdapter:
    """GauzMem 适配器 - 冗余挂载模式"""

    def __init__(self, enabled: bool = True):
        """
        初始化适配器

        Args:
            enabled: 是否启用 GauzMem（默认启用，如果客户端可用）
        """
        self.enabled = enabled and GAUZ_AVAILABLE
        self.client = None

        if self.enabled:
            try:
                # 获取 API URL，确保包含 /api/v1
                api_url = os.getenv("GAUZ_MEM_API_URL", "http://localhost:8000/api/v1")
                if not api_url.endswith("/api/v1"):
                    api_url = api_url.rstrip("/") + "/api/v1"

                # 直接传递参数给客户端
                self.client = GauzMemoryClient(
                    api_url=api_url,
                    api_key=os.getenv("GAUZ_MEM_API_KEY", "test_key"),
                    project_id=os.getenv("GAUZ_MEM_PROJECT_ID", "chatbot")
                )
                print("✅ GauzMem 适配器已启用")
            except Exception as e:
                print(f"⚠️ GauzMem 初始化失败: {e}")
                self.enabled = False

    async def recall_memories(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        从 GauzMem 召回相关记忆

        Args:
            query: 查询文本
            top_k: 返回记忆数量

        Returns:
            记忆列表，格式：[{"content": "...", "quote": "..."}]
        """
        if not self.enabled:
            return []

        import time
        overall_start = time.time()

        try:
            print(f"🔍 [GauzMem] 开始召回记忆 (query={query[:50]}..., top_k={top_k})")

            # 使用 asyncio.to_thread 在线程池中运行同步的 HTTP 请求
            api_start = time.time()
            memories = await asyncio.to_thread(
                self.client.recall,
                query=query,
                top_k=top_k
            )
            api_duration = time.time() - api_start
            print(f"  ⏱️  API 调用耗时: {api_duration:.2f}s")

            # 转换为统一格式
            convert_start = time.time()
            result = []
            for memory in memories:
                result.append({
                    "content": memory.content,
                    "quote": memory.quote,
                    "source": "gauz_mem"
                })
            convert_duration = time.time() - convert_start
            print(f"  ⏱️  数据转换耗时: {convert_duration:.3f}s")

            overall_duration = time.time() - overall_start
            print(f"✅ GauzMem 召回 {len(result)} 条记忆 (总耗时: {overall_duration:.2f}s)")

            # 性能警告
            if api_duration > 10:
                print(f"⚠️  [性能警告] API 调用耗时过长: {api_duration:.2f}s")

            return result

        except Exception as e:
            error_msg = str(e)
            overall_duration = time.time() - overall_start
            if "timeout" in error_msg.lower():
                print(f"⏳ GauzMem 召回超时（后台处理中）- 耗时: {overall_duration:.2f}s")
            else:
                print(f"⚠️ GauzMem 召回失败: {e} - 耗时: {overall_duration:.2f}s")
            return []

    async def store_message(
        self,
        text: str,
        user_id: str,
        session_id: str,
        role: str = "user",
        turn: int = 1
    ) -> Optional[str]:
        """
        存储消息到 GauzMem

        Args:
            text: 消息内容
            user_id: 用户 ID
            session_id: 会话 ID
            role: 角色（user/assistant）
            turn: 对话轮次

        Returns:
            chunk_id 或 None（如果失败）
        """
        if not self.enabled:
            return None

        try:
            # 映射 role 到 speaker
            speaker = "user" if role == "user" else "agent"

            # 使用 asyncio.to_thread 在线程池中运行同步的 HTTP 请求
            # 避免阻塞 event loop
            result = await asyncio.to_thread(
                self.client.store_message,
                text=text,
                user_id=user_id,
                run_id=session_id,
                speaker=speaker,
                turn=turn,
                async_mode=True
            )

            print(f"✅ GauzMem 存储消息: chunk_id={result.chunk_id}")
            return result.chunk_id

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                print(f"⏳ GauzMem 存储超时（后台处理中）")
                return "pending"
            else:
                print(f"⚠️ GauzMem 存储失败: {e}")
                return None
