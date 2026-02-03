# Skill 开发指南

## 🎯 概述

本指南帮助你快速开发新的 Skill，并集成到主系统中。

## 📋 核心理念

**"先专注开发，后标准化适配"**

- 在 `skills-dev/` 独立开发，不影响主系统
- 专注于 prompt + tools + 数据逻辑
- 开发完成后，一键发布到生产环境

---

## 🚀 快速开始

### 1. 创建新 Skill

```bash
python scripts/skill_dev.py create your_skill_id
```

这会创建以下目录结构：

```
skills-dev/your_skill_id/
├── skill.yaml              # Skill 配置
├── prompt.md               # Prompt 模板
├── tools.py                # 工具实现
├── models.py               # 数据模型（可选）
├── services/               # 业务逻辑层（可选）
├── repositories/           # 数据访问层（可选）
├── tests/                  # 测试文件
│   ├── test_tools.py       # 单元测试
│   └── test_integration.py # 集成测试
└── README.md               # 开发文档
```

### 2. 配置 Skill 信息

编辑 `skill.yaml`：

```yaml
id: your_skill_id
name: 你的技能名称
version: 0.1.0
description: 简短描述

prompt_file: prompt.md

tools:
  - name: create_item
    module: tools
    function: create_item
    description: 创建新项目

database:
  tables:
    - table_name: items
      description: 项目表

dependencies:
  - core.memory
  - core.embedding
```

### 3. 编写 Prompt

编辑 `prompt.md`，定义 Skill 的行为规则：

```markdown
# 你的 Skill Prompt

## 角色定义
你是一个专门负责 [具体领域] 的智能助手。

## 核心能力
1. 能力描述...

## 工具使用规则
- 工具使用场景...
```

---

## 🛠️ 开发工具实现

### 基本结构

编辑 `tools.py`：

```python
def your_tool(param1: str, param2: int = None) -> Dict[str, Any]:
    """
    工具描述

    Args:
        param1: 参数描述
        param2: 参数描述（可选）

    Returns:
        Dict[str, Any]: {"success": bool, "data": any, "error": str}
    """
    try:
        # 1. 参数验证
        if not param1:
            return {"success": False, "error": "参数不能为空"}

        # 2. 业务逻辑
        result = do_something(param1)

        # 3. 返回结果
        return {"success": True, "data": result}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 工具注册

在 `tools.py` 底部添加：

```python
TOOL_DEFINITIONS = [
    {
        "name": "your_tool",
        "description": "工具功能描述",
        "input_schema": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数描述"
                }
            },
            "required": ["param1"]
        }
    }
]
```

---

## 💾 数据层开发（可选）

### 1. 定义数据模型

编辑 `models.py`：

```python
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database.connection import Base
import uuid

class YourModel(Base):
    __tablename__ = "your_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2. 创建 Repository

在 `repositories/` 创建数据访问层：

```python
from .base_repository import BaseRepository
from ..models import YourModel

class YourRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, YourModel)

    def find_by_name(self, name: str):
        return self.session.query(YourModel).filter(
            YourModel.name == name
        ).first()
```

### 3. 创建 Service

在 `services/` 创建业务逻辑层：

```python
from ..repositories.your_repository import YourRepository

class YourService:
    def __init__(self, session):
        self.repository = YourRepository(session)

    def create_item(self, name: str):
        # 业务逻辑
        return self.repository.create(name=name)
```

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python scripts/skill_dev.py test your_skill_id
```

### 编写单元测试

编辑 `tests/test_tools.py`：

```python
from tools import your_tool

def test_your_tool():
    result = your_tool("test")
    assert result["success"] == True
    print(f"✅ 测试通过: {result}")
```

### 编写集成测试

编辑 `tests/test_integration.py`：

```python
from src.core.agent.memory_driven_agent import MemoryDrivenAgent

def test_skill_integration():
    agent = MemoryDrivenAgent(session_id="test")
    response = agent.chat("测试你的 skill")
    print(f"回复: {response}")
```

---

## 📦 发布流程

### 1. 注册到数据库

```bash
python scripts/skill_dev.py register your_skill_id
```

这会：
- 生成 prompt 的 embedding
- 注册到 `skills` 表

### 2. 发布到生产环境

```bash
python scripts/skill_dev.py publish your_skill_id
```

这会：
1. 注册到数据库
2. 创建数据库表（如果有 models.py）
3. 复制到 `src/skills/your_skill_id/`

### 3. 验证

启动主系统测试：

```bash
python chat.py
```

---

## 📝 最佳实践

### 1. Prompt 编写

- **清晰的角色定义**：明确 skill 的职责范围
- **具体的工具规则**：说明何时使用哪个工具
- **简洁的交互风格**：避免冗长的回复

### 2. 工具设计

- **单一职责**：每个工具只做一件事
- **统一返回格式**：`{"success": bool, "data": any, "error": str}`
- **完善的错误处理**：捕获异常并返回友好的错误信息

### 3. 数据设计

- **合理的表结构**：根据业务需求设计
- **使用 UUID**：作为主键
- **添加时间戳**：`created_at` 和 `updated_at`

### 4. 测试

- **先写测试**：TDD 开发模式
- **独立测试**：不依赖主系统
- **覆盖边界情况**：测试异常输入

---

## 🔍 调试技巧

### 1. 查看 Skill 是否被触发

在 agent 中添加日志：

```python
print(f"Selected skill: {selected_skill_id}")
```

### 2. 查看工具调用

在 tools.py 中添加日志：

```python
print(f"Tool called: {tool_name}, params: {params}")
```

### 3. 查看数据库

```bash
psql -d your_database
SELECT * FROM skills WHERE id = 'your_skill_id';
```

---

## 🎯 示例：Writing Skill

参考 `skills-dev/writing/` 查看完整示例。

---

## ❓ 常见问题

### Q: Skill 没有被触发？
A: 检查 prompt embedding 是否生成，尝试重新 register。

### Q: 工具调用失败？
A: 检查 TOOL_DEFINITIONS 格式是否正确。

### Q: 数据库表创建失败？
A: 检查 models.py 中的表定义是否正确。

---

## 📚 参考资料

- [新架构文档](./new_architecture.md)
- [Skill 模板](../skills-dev/SKILL_TEMPLATE/)
- [Todo Skill 示例](../src/skills/todo/)
