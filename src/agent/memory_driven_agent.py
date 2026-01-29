"""
记忆驱动 Agent - 统一的单层 Agent

核心特性：
1. 基于记忆动态构建 Prompt 和工具集
2. 自动压缩对话历史
3. 技能领域识别和记忆检索
4. 流式输出支持
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
import json

from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.state import AgentState, get_session_manager
from src.llm.deepseek_client import DeepSeekClient
from src.services.memory_service import MemoryService
from src.services.compression_service import CompressionService
from src.services.skill_memory_service import SkillMemoryService
from src.tools.setup import initialize_tools
from src.tools.registry import get_tool_registry


class MemoryDrivenAgent:
    """记忆驱动的统一 Agent"""

    def __init__(self, db: AsyncSession, use_reasoner: bool = False):
        """
        初始化 Agent

        Args:
            db: 数据库会话
            use_reasoner: 是否使用 reasoner 模式
        """
        self.db = db
        self.llm_client = DeepSeekClient(use_reasoner=use_reasoner)
        self.session_manager = get_session_manager()
        self.max_iterations = 20

        # 服务层
        self.memory_service = MemoryService(db)
        self.compression_service = CompressionService(db)
        self.skill_memory_service = SkillMemoryService(db)

        # 工具注册表
        initialize_tools()  # 初始化工具
        self.tool_registry = get_tool_registry()

        # 配置
        self.compression_threshold = 15  # 对话压缩阈值

    async def process_message(
        self,
        user_message: str,
        session_id: Optional[UUID] = None,
        stream_callback=None
    ) -> Dict[str, Any]:
        """
        处理用户消息

        Args:
            user_message: 用户消息
            session_id: 会话 ID
            stream_callback: 流式输出回调

        Returns:
            处理结果
        """
        # 获取或创建会话
        if session_id:
            state = self.session_manager.get_session(session_id)
            if not state:
                state = self.session_manager.create_session()
        else:
            state = self.session_manager.create_session()

        # 添加用户消息
        state.add_message("user", user_message)

        try:
            # 1. 检查是否需要压缩
            await self._check_and_compress(state)

            # 2. 识别技能领域
            skill_domain = self.skill_memory_service.identify_skill_domain(user_message)

            # 3. 检索技能记忆
            memories = await self.skill_memory_service.retrieve_skill_memories(
                user_request=user_message,
                skill_domain=skill_domain,
                top_k=5
            )

            # 4. 构建消息历史
            messages = self._build_messages(state, skill_domain, memories)

            # 5. 获取工具集
            tools = self.tool_registry.get_tool_schemas(skill_domain)

            # 6. 执行 Agent 循环
            result = await self._agent_loop(
                state=state,
                messages=messages,
                tools=tools,
                stream_callback=stream_callback
            )

            return {
                "success": True,
                "text": result["text"],
                "session_id": str(state.session_id),
                "iterations": result["iterations"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": str(state.session_id)
            }

    def _build_messages(
        self,
        state: AgentState,
        skill_domain: Optional[str],
        memories: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        构建消息历史（包含 system prompt + 记忆）

        Args:
            state: 会话状态
            skill_domain: 技能领域
            memories: 检索到的记忆

        Returns:
            消息列表
        """
        # 构建 system prompt
        system_prompt = self._build_system_prompt(skill_domain, memories)

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]

        # 添加对话历史
        for msg in state.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return messages

    def _build_system_prompt(
        self,
        skill_domain: Optional[str],
        memories: Dict[str, Any]
    ) -> str:
        """
        动态构建 system prompt

        Args:
            skill_domain: 技能领域
            memories: 检索到的记忆

        Returns:
            system prompt
        """
        from src.agent.prompts import build_agent_prompt
        return build_agent_prompt(skill_domain, memories)

    async def _agent_loop(
        self,
        state: AgentState,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        stream_callback=None
    ) -> Dict[str, Any]:
        """
        Agent 主循环

        Args:
            state: 会话状态
            messages: 消息历史
            tools: 工具列表
            stream_callback: 流式输出回调

        Returns:
            执行结果
        """
        iteration = 0
        accumulated_text = ""

        while iteration < self.max_iterations:
            iteration += 1

            # 调用 LLM
            response = await self.llm_client.chat_completion(
                messages=messages,
                tools=tools,
                stream=False
            )

            # 提取响应内容
            content = response.choices[0].message.content or ""
            tool_calls = response.choices[0].message.tool_calls

            # 输出文本内容
            if content and stream_callback:
                stream_callback('text', content)
            accumulated_text += content

            # 如果没有工具调用，结束循环
            if not tool_calls:
                # 添加助手消息到历史
                state.add_message("assistant", content)
                break

            # 处理工具调用
            tool_results = await self._execute_tools(
                tool_calls=tool_calls,
                stream_callback=stream_callback
            )

            # 添加助手消息（包含工具调用）到消息列表
            messages.append({
                "role": "assistant",
                "content": content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })

            # 添加工具结果消息
            for tool_call, result in zip(tool_calls, tool_results):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

            # 保存到会话状态
            state.add_message("assistant", content, tool_calls=tool_calls)

        return {
            "text": accumulated_text,
            "iterations": iteration
        }

    async def _execute_tools(
        self,
        tool_calls: List[Any],
        stream_callback=None
    ) -> List[Dict[str, Any]]:
        """
        执行工具调用

        Args:
            tool_calls: 工具调用列表
            stream_callback: 流式输出回调

        Returns:
            工具执行结果列表
        """
        results = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # 输出工具调用可视化
            if stream_callback:
                viz_text = self.tool_registry.format_visualization(
                    tool_name=function_name,
                    arguments=arguments,
                    stage="calling"
                )
                stream_callback('tool_call', viz_text + '\n')

            # 执行工具
            result = await self.tool_registry.execute_tool(
                tool_name=function_name,
                db=self.db,
                **arguments
            )

            # 输出工具结果可视化
            if stream_callback:
                if result.get("success"):
                    viz_text = self.tool_registry.format_visualization(
                        tool_name=function_name,
                        arguments={**arguments, **result.get("data", {})},
                        stage="success"
                    )
                else:
                    viz_text = self.tool_registry.format_visualization(
                        tool_name=function_name,
                        arguments={**arguments, "error": result.get("error", "")},
                        stage="error"
                    )
                stream_callback('tool_result', viz_text + '\n\n')

            results.append(result)

        return results

    async def _check_and_compress(self, state: AgentState) -> None:
        """
        检查是否需要压缩对话历史

        Args:
            state: 会话状态
        """
        try:
            # 获取当前对话历史
            conversation_history = []
            for msg in state.conversation_history:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # 检查是否需要压缩
            if self.compression_service.should_compact(
                conversation_history,
                threshold=self.compression_threshold
            ):
                print(f"对话历史达到 {len(conversation_history)} 轮，触发压缩...")

                # 执行压缩
                result = await self.compression_service.compact_and_memorize(
                    conversation_history=conversation_history,
                    session_id=str(state.session_id)
                )

                print(f"压缩完成: 写入 {result['sources_written']} 条对话，提取 {result['facts_extracted']} 个事实")

                # 清理旧的对话历史，只保留最近 5 轮
                state.conversation_history = state.conversation_history[-5:]

        except Exception as e:
            # 压缩失败不应该影响主流程
            print(f"对话压缩失败: {e}")

