"""
压缩服务 - 负责对话压缩和事实提取

功能：
1. 检测是否需要压缩（基于 token 数量）
2. 使用 LLM 提取事实
3. 写入记忆系统
"""
from typing import List, Dict, Any
import json
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.llm.deepseek_client import DeepSeekClient
from src.core.memory.memory_service import MemoryService


class CompressionService:
    """压缩服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_client = DeepSeekClient(use_reasoner=False)  # 使用 chat 模式
        self.memory_service = MemoryService(db)

    def should_compact(self, conversation_history: List[Dict], threshold: int = 15) -> bool:
        """
        判断是否需要压缩

        Args:
            conversation_history: 对话历史
            threshold: 阈值（对话轮数）

        Returns:
            是否需要压缩
        """
        return len(conversation_history) > threshold

    async def extract_facts(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """
        使用 LLM 从对话中提取事实

        Args:
            conversation_history: 对话历史

        Returns:
            提取的事实和元数据
        """
        # 格式化对话
        conversation_text = self._format_conversation(conversation_history)

        # 构建提取 prompt
        extraction_prompt = f"""
从以下对话中提取客观事实。

对话内容：
{conversation_text}

提取规则：
1. 只记录客观发生的事情，不做推断
2. 使用主谓宾结构描述事实
3. 记录工具调用的具体信息
4. 记录交互的具体流程

事实类型：
- action: 用户或助手执行的动作
- tool_call: 工具调用及其参数
- result: 操作的结果

输出格式（JSON）：
{{
    "facts": [
        {{
            "text": "用户请求创建任务",
            "type": "action",
            "domain": "todo"
        }},
        {{
            "text": "助手调用 create_task 工具，参数 title='学习记忆驱动的技能系统'",
            "type": "tool_call",
            "domain": "todo"
        }},
        {{
            "text": "任务创建成功",
            "type": "result",
            "domain": "todo"
        }}
    ]
}}

只输出 JSON，不要其他内容。
"""

        # 调用 LLM
        messages = [
            {"role": "user", "content": extraction_prompt}
        ]

        response = await self.llm_client.chat_completion(
            messages=messages,
            temperature=0.3,
            stream=False
        )

        # 解析响应
        content = response.choices[0].message.content

        # 去除可能的 markdown 代码块标记
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]  # 去掉 ```json
        elif content.startswith('```'):
            content = content[3:]  # 去掉 ```
        if content.endswith('```'):
            content = content[:-3]  # 去掉结尾的 ```
        content = content.strip()

        try:
            extracted = json.loads(content)
            return extracted
        except json.JSONDecodeError as e:
            # 如果解析失败，打印原始内容用于调试
            print(f"JSON 解析失败: {e}")
            print(f"LLM 原始返回内容:\n{content}")
            return {"facts": []}

    def _format_conversation(self, conversation_history: List[Dict]) -> str:
        """格式化对话历史为文本"""
        lines = []
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # 处理工具调用
            if msg.get("tool_calls"):
                tool_calls_str = json.dumps(msg["tool_calls"], ensure_ascii=False)
                lines.append(f"{role}: {content}\n[Tool Calls: {tool_calls_str}]")
            else:
                lines.append(f"{role}: {content}")

        return "\n\n".join(lines)

    async def compact_and_memorize(
        self,
        conversation_history: List[Dict],
        session_id: str
    ) -> Dict[str, Any]:
        """
        压缩对话并写入记忆系统

        Args:
            conversation_history: 对话历史
            session_id: 会话ID

        Returns:
            压缩结果统计
        """
        # 1. 写入对话到 mem_source
        source_ids = []
        for turn, msg in enumerate(conversation_history):
            source_id = await self.memory_service.write_conversation(
                session_id=session_id,
                turn=turn,
                speaker=msg.get("role", "unknown"),
                content=msg.get("content", ""),
                tool_calls=msg.get("tool_calls"),
                tool_results=msg.get("tool_results")
            )
            source_ids.append(source_id)

        # 2. 提取事实
        extracted = await self.extract_facts(conversation_history)

        # 3. 写入事实到 facts 表
        fact_ids = []
        for fact in extracted.get("facts", []):
            fact_id = await self.memory_service.write_fact(
                fact_text=fact["text"],
                source_ids=source_ids,
                fact_type=fact.get("type"),
                domain=fact.get("domain"),
                confidence=fact.get("confidence", 1.0)
            )
            fact_ids.append(fact_id)

        return {
            "sources_written": len(source_ids),
            "facts_extracted": len(fact_ids)
        }
