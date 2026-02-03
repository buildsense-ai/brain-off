"""
集成测试

测试 skill 在完整 agent 环境中的表现。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.database.session import get_session
from src.core.agent.memory_driven_agent import MemoryDrivenAgent


def test_skill_integration():
    """测试 skill 集成"""
    print("🧪 测试 Skill 集成...\n")

    # 创建 agent
    session = get_session()
    agent = MemoryDrivenAgent(session=session, session_id="test_skill")

    # 测试用例
    test_cases = [
        "你好",  # 测试非 skill 场景
        "帮我测试这个 skill",  # 测试 skill 触发
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"📝 测试 {i}: {user_input}")
        response = agent.chat(user_input)
        print(f"🤖 回复: {response}\n")

    print("✅ 集成测试完成！")


if __name__ == "__main__":
    test_skill_integration()
