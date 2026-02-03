# {Skill Name} - 开发文档

## 📋 Skill 信息

- **ID**: `your_skill_id`
- **名称**: 你的技能名称
- **版本**: 0.1.0
- **状态**: 🚧 开发中

## 🎯 功能描述

简要描述这个 skill 的核心功能和使用场景。

## 🛠️ 工具列表

### 1. `example_tool`
- **功能**: 工具功能描述
- **参数**:
  - `param1` (string, 必需): 参数描述
  - `param2` (integer, 可选): 参数描述
- **返回**: 返回值描述

## 📊 数据模型

### ExampleModel
- `id`: UUID, 主键
- `name`: 名称
- `description`: 描述
- `created_at`: 创建时间

## 🧪 测试

### 运行单元测试
```bash
cd skills-dev/your_skill_id
python tests/test_tools.py
```

### 运行集成测试
```bash
cd skills-dev/your_skill_id
python tests/test_integration.py
```

## 📝 开发日志

### 2026-01-30
- 初始化 skill 结构
- 实现基础工具

## 🚀 发布

开发完成后，运行：
```bash
python scripts/skill_dev.py publish your_skill_id
```
