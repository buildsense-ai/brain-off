# 记忆驱动技能系统 (Memory-Driven Skill System) 架构概览

## 1. 核心哲学：Memory as Skill
在传统的 Agent 设计中，技能（Skill）通常是预定义的、静态的。本系统核心理念是将“记忆”与“技能”合二为一：
- **技能不再是死代码**，而是从历史经验中动态生成的“经验模版”。
- **Skill = System Prompt (经验) + Tool Set (工具) + Action Traces (路径)**。

## 2. 系统核心组件

### 2.1 进化式记忆仓库 (Evolutionary Memory)
存储原子化的事实（Facts）和执行轨迹（Traces），而非单纯的对话日志。
- **Atomic Facts**: 最小单元的事实描述（如：用户偏好、业务规则）。
- **Action Traces**: 捕获“尝试与错误”的链条。
  - *Relation: `RESOLVED_FAILURE`* - 记录错误是如何被修复的。
  - *Relation: `SEQUENCE`* - 记录成功的工具调用顺序。
  - *Relation: `CONSTRAINT`* - 记录导致失败的边界条件。

### 2.2 动态技能加载器 (Dynamic Skill Loader)
基于用户 Query，实时从记忆仓库中“编织”技能上下文。
- **意图感知检索**: 识别当前需求属于哪个领域（如：写作、Todo）。
- **JIT Skill 合成**: 类似即时编译（JIT），将碎片化的记忆片段拼凑成一个临时的 Skill Prompt。

### 2.3 技能固化引擎 (Skill Solidification Engine) - *Key Innovation*
解决“临时拼凑不稳定且慢”的问题，引入冷热数据管理：
- **热点识别**: 监控高频且高成功率的执行路径。
- **自动固化**: 后台 LLM（教练模型）对碎片记忆进行深度复盘，生成结构化的 `Stable_Skill.md`（类似于 Anthropic 范式的 Skill 文件）。
- **版本演进**: 当新的 Try & Error 证明旧模版已过时，触发模版自动更新。

## 3. 动态 Skill Prompt 结构
模仿并扩展了现代 Agent 的 Skill 定义，将“静态定义”与“动态经验”解耦：

| 模块 | 类型 | 描述 |
| :--- | :--- | :--- |
| **Static Header** | 静态 | 技能职责描述、基础指令、固定工具集。 |
| **Dynamic Experience** | **动态** | **核心区**。基于记忆生成的“红榜”（成功路径）与“黑榜”（避坑指南）。 |
| **Action Traces** | **动态** | 具体的 Few-shot 案例，展示“错误路径 -> 修复方案 -> 最终结果”。 |
| **Active Context** | 运行时 | 当前任务特有的背景数据。 |

## 4. 核心工作流

### 4.1 响应链路 (Execution Path)
1. **Query 检索**: 检索通用背景（Query Context）和技能经验（Skill Memories）。
2. **Skill 加载**: 
   - *命中快路径*: 加载已固化的 `Stable Skill`。
   - *命慢路径*: 动态合成临时 Skill。
3. **ReAct 循环**: Agent 在 Skill 的指导下，利用动态挂载的工具集完成任务。

### 4.2 进化链路 (Learning Path)
1. **捕获 (Capture)**: 完整记录工具调用的思考过程与结果。
2. **压缩 (Compact)**: 在上下文窗口满时，提取原子事实与 Action Traces。
3. **固化 (Solidify)**: 异步任务分析高频模式，将碎片记忆升格为固化的技能模版。

## 5. 架构优势
- **自适应性**: 系统能够从失败中学习，自动规避曾经犯过的错误。
- **性能平衡**: 通过“冷热固化”机制，既保留了动态灵活性，又保证了高频场景的响应速度。
- **低维护成本**: 开发者只需定义基础工具，复杂的业务流和避坑逻辑由 Agent 在交互中自动沉淀。
