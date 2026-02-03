# GauzAssist GUI 版本

独立的 Gradio GUI 界面，复用 CLI 的核心逻辑。

## 启动方式

```bash
# 方式 1: 使用启动脚本
./gui/start_gui.sh

# 方式 2: 直接运行
python gui/gradio_app.py
```

## 特性

- ✅ 复用 CLI 的 Agent 核心逻辑
- ✅ 共享数据库和 GauzMem 记忆
- ✅ Web 界面，易于使用
- ✅ 与 CLI 完全独立，互不干扰
- ✅ 原生异步支持（Gradio）
- ✅ 多标签页界面（聊天 + 仪表盘）

## 架构

```
gui/
├── gradio_app.py         # 主应用（Gradio）
├── test_gradio.py        # 测试脚本
├── start_gui.sh          # 启动脚本
├── components/           # GUI 组件（待扩展）
├── utils/                # GUI 工具（待扩展）
└── requirements.txt      # GUI 依赖
```

## 与 CLI 的关系

- **共享**: Agent、记忆系统、数据库
- **独立**: 界面代码、会话管理
- **互通**: CLI 和 GUI 的对话历史可以互相看到
