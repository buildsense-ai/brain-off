"""
System prompts for the AI agent.
"""
from typing import List, Dict, Any


# 基础 Agent Prompt（所有技能共享）
BASE_AGENT_PROMPT = """你是一个智能助手，通过对话帮助用户完成各种任务。

在 CLI 环境下，请保持简洁、直接的对话风格：
- 避免使用过多的 Markdown 格式（如粗体、斜体等）
- 回复简明扼要，直接给出结果
- 自然对话，不需要过度解释过程"""


def build_agent_prompt(
    skill_prompt: str,
    facts: List[Dict[str, Any]]
) -> str:
    """
    动态构建 Agent Prompt

    Args:
        skill_prompt: 技能 prompt（从数据库读取）
        facts: 检索到的记忆

    Returns:
        完整的 system prompt
    """
    prompt_parts = [BASE_AGENT_PROMPT]

    # 添加技能特定 Prompt
    if skill_prompt:
        prompt_parts.append("\n" + skill_prompt)

    # 添加相关记忆
    if facts:
        prompt_parts.append("\n## 相关记忆（过往经验）")
        for fact in facts:
            prompt_parts.append(f"- {fact['fact_text']}")

    return "\n".join(prompt_parts)
