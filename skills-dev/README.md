# Skills 开发目录

## 🎯 目录说明

这是 Skill 的独立开发环境，让你可以专注于 agent 逻辑开发，无需担心集成问题。

## 📁 目录结构

```
skills-dev/
├── SKILL_TEMPLATE/      # Skill 模板（不要修改）
├── writing/             # 示例 skill
└── your_skill/          # 你的新 skill
```

## 🚀 快速开始

### 1. 创建新 Skill

```bash
python scripts/skill_dev.py create your_skill_id
```

### 2. 开发 Skill

进入 skill 目录，专注开发：

```bash
cd skills-dev/your_skill_id
```

编辑以下文件：
- `skill.yaml` - 配置信息
- `prompt.md` - Prompt 模板
- `tools.py` - 工具实现

### 3. 测试 Skill

```bash
python scripts/skill_dev.py test your_skill_id
```

### 4. 发布到生产环境

```bash
python scripts/skill_dev.py publish your_skill_id
```

## 📚 文档

- [Skill 开发指南](../docs/skill_development_guide.md) - 完整开发文档
- [新架构文档](../docs/new_architecture.md) - 系统架构说明
- [Writing Skill 示例](./writing/) - 参考示例

## 💡 核心理念

**"先专注开发，后标准化适配"**

1. 在 `skills-dev/` 独立开发
2. 用独立测试快速迭代
3. 开发完成后一键发布
4. 自动集成到主系统

## 🛠️ 可用命令

```bash
# 创建新 skill
python scripts/skill_dev.py create <skill_id>

# 测试 skill
python scripts/skill_dev.py test <skill_id>

# 注册到数据库
python scripts/skill_dev.py register <skill_id>

# 发布到生产环境
python scripts/skill_dev.py publish <skill_id>
```

## 📝 示例

参考 `writing/` 目录查看完整的 skill 实现示例。
