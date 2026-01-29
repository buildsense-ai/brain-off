"""
技能记忆服务 - 负责技能相关的记忆检索和 Prompt 构建

功能：
1. 识别用户请求的技能类型（意图识别）
2. 检索技能相关的记忆
3. 动态构建技能 Prompt
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.memory_service import MemoryService


class SkillMemoryService:
    """技能记忆服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.memory_service = MemoryService(db)

        # 技能领域映射
        self.skill_domains = {
            "todo": ["任务", "待办", "todo", "task", "创建", "完成", "删除", "列出"],
            "writing": ["写作", "文章", "博客", "写", "编辑"],
            "learning": ["学习", "教程", "课程", "知识"],
        }

    def identify_skill_domain(self, user_request: str) -> Optional[str]:
        """
        识别用户请求的技能领域

        Args:
            user_request: 用户请求

        Returns:
            技能领域名称，如果无法识别则返回 None
        """
        user_request_lower = user_request.lower()

        # 简单的关键词匹配
        for domain, keywords in self.skill_domains.items():
            for keyword in keywords:
                if keyword in user_request_lower:
                    return domain

        return None

    async def retrieve_skill_memories(
        self,
        user_request: str,
        skill_domain: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        检索技能相关的记忆

        Args:
            user_request: 用户请求
            skill_domain: 技能领域（如果已知）
            top_k: 返回结果数量

        Returns:
            包含 facts 和 sources 的字典
        """
        # 如果没有指定领域，先识别
        if skill_domain is None:
            skill_domain = self.identify_skill_domain(user_request)

        # 检索记忆
        memories = await self.memory_service.retrieve_memories(
            query=user_request,
            top_k=top_k
        )

        # 如果指定了领域，过滤相关的 facts
        if skill_domain:
            filtered_facts = [
                fact for fact in memories['facts']
                if fact.get('domain') == skill_domain
            ]
            memories['facts'] = filtered_facts

        return memories

    def build_skill_prompt(
        self,
        base_prompt: str,
        memories: Dict[str, Any],
        skill_domain: Optional[str] = None
    ) -> str:
        """
        动态构建技能 Prompt

        Args:
            base_prompt: 基础 Prompt
            memories: 检索到的记忆
            skill_domain: 技能领域

        Returns:
            增强后的 Prompt
        """
        prompt_parts = [base_prompt]

        # 添加技能领域信息
        if skill_domain:
            prompt_parts.append(f"\n## 当前技能领域: {skill_domain}")

        # 添加相关记忆
        if memories['facts']:
            prompt_parts.append("\n## 相关记忆（过往经验）")
            for fact in memories['facts'][:5]:  # 最多 5 个
                prompt_parts.append(f"- {fact['fact_text']}")

        return "\n".join(prompt_parts)
