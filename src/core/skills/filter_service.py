"""
Filter Service - 使用 LLM 过滤 skills 和 facts
"""
from typing import List, Dict, Any
import json

from src.infrastructure.llm.deepseek_client import DeepSeekClient


class FilterService:
    """过滤服务 - 使用 LLM 过滤候选的 skills 和 facts"""

    def __init__(self):
        self.llm_client = DeepSeekClient(use_reasoner=False)
        self.filter_schema = self._build_filter_schema()

    def _build_filter_schema(self) -> Dict[str, Any]:
        """构建过滤 LLM 的 function calling schema"""
        return {
            "type": "function",
            "function": {
                "name": "select_skill_and_facts",
                "description": "根据用户请求选择最相关的技能和记忆",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "description": "最相关的技能 ID（只选 1 个，如果都不相关则返回空字符串）"
                        },
                        "fact_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "相关的记忆 ID 列表（可以多个）"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "选择理由（用于调试）"
                        }
                    },
                    "required": ["skill_id", "fact_ids", "reasoning"]
                }
            }
        }

    async def filter_skills_and_facts(
        self,
        user_query: str,
        candidate_skills: List[Dict],
        candidate_facts: List[Dict]
    ) -> Dict[str, Any]:
        """
        使用 LLM 过滤候选的 skills 和 facts

        Args:
            user_query: 用户输入
            candidate_skills: 候选技能列表
            candidate_facts: 候选记忆列表

        Returns:
            {
                "skill_id": "todo" or "",
                "fact_ids": [1, 2, 3],
                "reasoning": "..."
            }
        """
        # 构建过滤 prompt
        filter_prompt = self._build_filter_prompt(
            user_query,
            candidate_skills,
            candidate_facts
        )

        # 调用 LLM
        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": filter_prompt}],
            tools=[self.filter_schema],
            stream=False
        )

        # 解析结果
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            return {"skill_id": "", "fact_ids": [], "reasoning": "No tool call"}

        arguments = json.loads(tool_calls[0].function.arguments)
        return arguments

    def _build_filter_prompt(
        self,
        user_query: str,
        candidate_skills: List[Dict],
        candidate_facts: List[Dict]
    ) -> str:
        """构建过滤 prompt"""
        prompt_parts = [
            f"用户请求：{user_query}\n",
            "\n候选技能：",
            self._format_skills(candidate_skills),
            "\n候选记忆：",
            self._format_facts(candidate_facts),
            "\n请选择最相关的 1 个技能（如果都不相关则返回空字符串）和相关的记忆。"
        ]
        return "\n".join(prompt_parts)

    def _format_skills(self, skills: List[Dict]) -> str:
        """格式化 skills 列表"""
        if not skills:
            return "（无候选技能）"

        lines = []
        for skill in skills:
            lines.append(f"ID: {skill['id']}")
            lines.append(f"名称: {skill['name']}")
            lines.append(f"说明:\n{skill['prompt_template'][:500]}...")  # 截断到 500 字符
            lines.append("---")
        return "\n".join(lines)

    def _format_facts(self, facts: List[Dict]) -> str:
        """格式化 facts 列表"""
        if not facts:
            return "（无候选记忆）"

        lines = []
        for fact in facts:
            lines.append(f"ID: {fact['fact_id']}")
            lines.append(f"内容: {fact['fact_text']}")
            lines.append(f"领域: {fact.get('domain', 'N/A')}")
            lines.append("---")
        return "\n".join(lines)
