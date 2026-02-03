# 新架构文档

## 🎯 架构概览

本项目采用**模块化、记忆驱动**的架构设计，核心特点：

1. **Embedding-based Skill 检索** - 废弃关键词匹配，使用向量检索
2. **LLM 过滤层** - 智能过滤候选 skills 和 facts
3. **动态工具挂载** - 根据 skill 动态加载工具集
4. **独立的记忆系统** - 对话压缩和事实提取
5. **清晰的模块边界** - Core / Skills / Infrastructure

---

## 📦 目录结构

```
src/
├── core/                      # 核心系统
│   ├── memory/               # 记忆系统
│   │   ├── embedding_service.py
│   │   ├── memory_service.py
│   │   └── compression_service.py
│   │
│   ├── agent/                # Agent 系统
│   │   ├── memory_driven_agent.py
│   │   ├── prompts.py
│   │   └── state.py
│   │
│   └── skills/               # Skill 管理
│       ├── skill_service.py
│       ├── filter_service.py
│       └── tool_registry.py
│
├── skills/                    # 具体的 skills
│   └── todo/                 # Todo Skill
│       ├── tools.py          # 工具实现
│       ├── search_tools.py
│       └── setup.py          # 工具初始化
│
├── infrastructure/            # 基础设施
│   ├── config.py             # 配置管理
│   ├── database/
│   │   ├── models.py         # 数据模型
│   │   ├── connection.py
│   │   └── session.py
│   │
│   ├── llm/
│   │   └── deepseek_client.py
│   │
│   └── utils/
│       └── cli_colors.py
│
├── services/                  # Todo Skill 的服务层
│   └── search_service.py     # 任务搜索服务
│
└── repositories/              # Todo Skill 的数据访问层
    ├── base.py
    ├── task_repository.py
    └── tag_repository.py
```

---

## 🗄️ 数据库表结构

### 核心系统表

#### 1. skills 表
存储技能定义和配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(50) | 技能 ID（主键）|
| name | String(100) | 技能名称 |
| prompt_template | Text | Prompt 模板 |
| embedding | Vector(1024) | Prompt 的 embedding |
| tool_set | JSONB | 工具集列表 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 2. mem_source 表
存储对话历史（用于压缩）

| 字段 | 类型 | 说明 |
|------|------|------|
| source_id | Integer | 主键（自增）|
| session_id | String(255) | 会话 ID |
| turn | Integer | 对话轮次 |
| speaker | String(50) | 说话者 |
| content | Text | 对话内容 |
| tool_calls | JSONB | 工具调用 |
| tool_results | JSONB | 工具结果 |
| embedding | Vector(1024) | 内容的 embedding |
| created_at | DateTime | 创建时间 |

#### 3. facts 表
存储提取的事实

| 字段 | 类型 | 说明 |
|------|------|------|
| fact_id | Integer | 主键（自增）|
| fact_text | Text | 事实内容 |
| source_ids | Integer[] | 来源 ID 列表 |
| fact_type | String(50) | 事实类型 |
| domain | String(50) | 领域 |
| confidence | Float | 置信度 |
| embedding | Vector(1024) | 事实的 embedding |
| created_at | DateTime | 创建时间 |

---

### Todo Skill 的数据表

#### 4. tasks 表
任务数据

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| title | String(500) | 任务标题 |
| description | Text | 任务描述 |
| status | String(50) | 状态 |
| priority | String(20) | 优先级 |
| embedding | Vector(1024) | 任务的 embedding |
| metadata | JSONB | 元数据 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 5. tags 表
标签数据

#### 6. task_tags 表
任务-标签关联表

---

## 🔄 核心流程

### 用户消息处理流程

```
用户输入
   ↓
1. 对话压缩检查
   ↓
2. 生成 query embedding
   ↓
3. 并行检索
   ├─ retrieve_skills (top_k=3)
   └─ retrieve_facts (top_k=10)
   ↓
4. LLM 过滤
   ├─ 输入：user_query + candidate_skills + candidate_facts
   └─ 输出：{"skill_id": "todo", "fact_ids": [1,2,3]}
   ↓
5. 动态工具挂载
   ├─ 如果 skill_id 存在 → 加载 skill.tool_set
   └─ 否则 → 加载默认工具集
   ↓
6. 构建 messages
   ├─ system prompt = BASE_PROMPT + skill_prompt + facts
   └─ conversation_history
   ↓
7. Agent Loop
   ├─ LLM 调用
   ├─ 工具执行
   └─ 迭代直到完成
   ↓
返回结果
```

---

## ✅ 测试结果

新架构已通过完整测试：

```bash
🔧 初始化工具...
✅ 工具初始化完成

🤖 创建 Agent...
✅ Agent 创建完成

💬 测试 1: 简单问候
回复: 你好！我是你的智能助手...
Skill: (无 - 正确识别为非任务相关)

💬 测试 2: 创建任务
回复: 已创建任务：测试新架构
Skill: todo (正确识别)
工具调用: 2 次

✅ 所有测试通过！
```

---

## 🚀 快速开始

### 1. 初始化数据库

```bash
PYTHONPATH=/path/to/chatbot python scripts/init_new_db.py
```

### 2. 运行测试

```bash
PYTHONPATH=/path/to/chatbot python scripts/test_new_architecture.py
```

### 3. 启动 CLI

```bash
PYTHONPATH=/path/to/chatbot python chat.py
```

---

## 📝 总结

### ✅ 已完成

1. ✅ 模块化架构重构
2. ✅ Embedding-based skill 检索
3. ✅ LLM 过滤层
4. ✅ 动态工具挂载
5. ✅ 数据库表结构优化
6. ✅ 完整的测试验证
7. ✅ BASE_AGENT_PROMPT 简化（移除 skill 特定规则）

### 🎯 核心优势

1. **更准确的意图识别** - 向量检索 + LLM 过滤
2. **更清晰的模块边界** - Core / Skills / Infrastructure
3. **更灵活的扩展性** - 新增 skill 只需添加数据，无需改代码
4. **更独立的记忆系统** - 可以单独使用和优化
5. **更清晰的 Prompt 分层** - Base prompt 只管通用规则，skill prompt 管具体行为

### 🔮 未来优化方向

1. 添加更多 skills (writing, learning)
2. 优化 LLM 过滤层的性能
3. 添加 skill 置信度机制
4. 实现工具发现机制（tool_discovery）
5. 优化 todo skill prompt（移除过程词等）
