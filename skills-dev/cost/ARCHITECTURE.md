# 工程造价 Agent 架构设计

## 📐 系统概述

基于CAD图纸的智能工程量清单生成系统，结合结构化数据提取和多模态视觉理解。

## 🏗️ 分层架构

```
┌─────────────────────────────────────────────────┐
│           Agent 决策层 (LLM)                     │
│  - 规划分析流程                                   │
│  - 调用工具组合                                   │
│  - 生成清单内容                                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              工具层 (Tools)                      │
├─────────────────────────────────────────────────┤
│ 1. CAD数据工具    │ 2. 视觉理解工具              │
│ 3. 计划管理工具   │ 4. 清单编辑工具              │
│ 5. 知识检索工具   │ 6. 导出工具                  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            数据持久层 (Storage)                  │
│  - SQLite: 计划、清单、中间结果                  │
│  - FileSystem: CAD文件、图片、PDF                │
│  - Cache: 视觉分析结果                           │
└─────────────────────────────────────────────────┘
```

## 🔧 工具设计

### 1. CAD 数据工具

#### `load_cad_file`
- **功能**: 加载并解析CAD文件（DWG/DXF）
- **输入**: 文件路径
- **输出**: 文件元数据、图层列表、实体统计
- **技术**: ezdxf

#### `extract_cad_entities`
- **功能**: 提取特定类型的CAD实体
- **输入**: 文件ID、实体类型（LINE/CIRCLE/TEXT等）、图层过滤
- **输出**: 实体列表（坐标、属性、尺寸）
- **用途**: 提取墙体、门窗、柱子等

#### `calculate_cad_measurements`
- **功能**: 计算CAD实体的工程量
- **输入**: 实体列表、计算规则
- **输出**: 长度、面积、体积等
- **示例**: 墙体长度、房间面积、混凝土体积

### 2. 视觉理解工具

#### `convert_cad_to_image`
- **功能**: 将CAD转换为图片/PDF
- **输入**: CAD文件路径、图层选择、视图设置
- **输出**: 图片文件路径列表
- **技术**: matplotlib + ezdxf 或 AutoCAD API

#### `analyze_drawing_visual`
- **功能**: 多模态分析图纸视觉内容
- **输入**: 图片路径、分析目标（文字/符号/图例）
- **输出**: OCR文字、识别的符号、图例说明
- **技术**: Claude Vision API / GPT-4V

#### `extract_drawing_annotations`
- **功能**: 提取图纸标注和说明
- **输入**: 图片路径
- **输出**: 标注文字、尺寸标注、材料说明
- **用途**: 补充CAD数据中缺失的信息

### 3. 计划管理工具

#### `create_analysis_plan`
- **功能**: 创建图纸分析计划
- **输入**: 项目名称、图纸列表、分析目标
- **输出**: 计划ID、任务列表
- **存储**: SQLite

#### `update_plan_progress`
- **功能**: 更新计划执行进度
- **输入**: 计划ID、任务ID、状态、结果
- **输出**: 更新确认
- **用途**: 追踪分析进度、记录中间结果

#### `get_plan_context`
- **功能**: 获取计划上下文
- **输入**: 计划ID
- **输出**: 完整的计划状态、已完成任务、待办事项
- **用途**: Agent恢复上下文、继续分析

#### `add_plan_note`
- **功能**: 添加分析笔记
- **输入**: 计划ID、笔记内容、关联实体
- **输出**: 笔记ID
- **用途**: 记录发现、疑问、决策依据

### 4. 清单编辑工具

#### `create_boq_item`
- **功能**: 创建清单项目
- **输入**: 项目编码、名称、单位、工程量、单价
- **输出**: 清单项ID
- **存储**: SQLite

#### `update_boq_item`
- **功能**: 更新清单项目
- **输入**: 项目ID、更新字段
- **输出**: 更新确认

#### `create_sub_boq`
- **功能**: 创建子清单
- **输入**: 父清单ID、子清单名称
- **输出**: 子清单ID
- **用途**: 分部分项、专业分类

#### `query_boq`
- **功能**: 查询清单
- **输入**: 过滤条件、排序规则
- **输出**: 清单项列表、统计汇总
- **用途**: 检查、审核、统计

#### `calculate_boq_total`
- **功能**: 计算清单合价
- **输入**: 清单ID
- **输出**: 分项合价、总价
- **用途**: 成本估算

### 5. 知识检索工具

#### `search_quota_standard`
- **功能**: 搜索定额标准
- **输入**: 关键词、专业类别
- **输出**: 定额编码、工作内容、计量规则
- **数据源**: 本地定额库 + 互联网

#### `search_material_price`
- **功能**: 查询材料价格
- **输入**: 材料名称、规格、地区
- **输出**: 市场价、信息价
- **数据源**: 价格数据库 + 网络爬虫

#### `search_construction_spec`
- **功能**: 搜索施工规范
- **输入**: 规范名称、条款关键词
- **输出**: 规范内容、计算规则
- **用途**: 指导工程量计算

#### `web_search`
- **功能**: 通用网络搜索
- **输入**: 搜索关键词
- **输出**: 搜索结果摘要
- **用途**: 查询不确定的信息

### 6. 导出工具

#### `export_boq_to_excel`
- **功能**: 导出清单到Excel
- **输入**: 清单ID、模板选择
- **输出**: Excel文件路径
- **技术**: openpyxl
- **格式**: 符合国标清单格式

#### `export_analysis_report`
- **功能**: 导出分析报告
- **输入**: 计划ID
- **输出**: PDF/Word报告
- **内容**: 图纸分析过程、工程量计算、清单汇总

## 📊 数据模型

### CADFile (CAD文件)
- id: UUID
- filename: 文件名
- file_path: 存储路径
- file_type: DWG/DXF
- metadata: JSONB (图层、比例、单位等)
- created_at: 上传时间

### AnalysisPlan (分析计划)
- id: UUID
- project_name: 项目名称
- cad_files: JSONB (关联的CAD文件列表)
- tasks: JSONB (任务列表)
- status: 状态 (pending/in_progress/completed)
- context: JSONB (上下文数据)
- created_at, updated_at

### PlanNote (计划笔记)
- id: UUID
- plan_id: 关联计划
- content: 笔记内容
- note_type: 类型 (discovery/question/decision)
- related_entity: JSONB (关联的CAD实体)
- created_at

### BOQItem (清单项目)
- id: UUID
- plan_id: 关联计划
- parent_id: 父项目ID (用于子清单)
- code: 项目编码
- name: 项目名称
- unit: 单位
- quantity: 工程量
- unit_price: 单价
- total_price: 合价
- source: 来源 (CAD实体ID、计算规则)
- metadata: JSONB (附加信息)
- created_at, updated_at

### VisualAnalysis (视觉分析结果)
- id: UUID
- cad_file_id: 关联CAD文件
- image_path: 图片路径
- analysis_result: JSONB (OCR、识别结果)
- created_at

## 🔄 典型工作流程

### 流程1: 新项目分析

```
1. load_cad_file()
   → 加载CAD文件，获取基本信息

2. create_analysis_plan()
   → 创建分析计划

3. convert_cad_to_image()
   → 转换为图片，便于视觉分析

4. analyze_drawing_visual()
   → 多模态分析，理解图纸内容

5. extract_cad_entities()
   → 提取结构化数据（墙、门、窗等）

6. calculate_cad_measurements()
   → 计算工程量

7. search_quota_standard()
   → 查询定额，确定清单项

8. create_boq_item()
   → 创建清单项目

9. calculate_boq_total()
   → 计算总价

10. export_boq_to_excel()
    → 导出Excel清单
```

### 流程2: 增量更新

```
1. get_plan_context()
   → 恢复之前的分析上下文

2. update_boq_item()
   → 修改清单项

3. add_plan_note()
   → 记录修改原因

4. export_boq_to_excel()
   → 重新导出
```

## 🎨 Agent Prompt 设计要点

### 角色定位
- 专业的工程造价师
- 熟悉CAD图纸
- 了解定额规范
- 细致、严谨

### 工作原则
1. **先理解后计算**: 先用视觉工具理解图纸整体，再提取数据
2. **记录决策过程**: 用 plan_note 记录每个判断依据
3. **增量式工作**: 分步骤完成，随时保存进度
4. **主动查询**: 遇到不确定的定额、规范，主动搜索
5. **交叉验证**: CAD数据 + 视觉分析 互相验证

### 错误处理
- CAD文件损坏 → 提示用户
- 识别不清 → 请求人工确认
- 定额缺失 → 搜索或标记待定

## 🚀 技术栈

### Python 依赖
```
ezdxf          # CAD文件读取
matplotlib     # CAD可视化
Pillow         # 图像处理
openpyxl       # Excel导出
anthropic      # Claude API (视觉分析)
sqlalchemy     # 数据库ORM
```

### 可选增强
- `pdf2image`: PDF转图片
- `pytesseract`: 本地OCR备选
- `pandas`: 数据处理
- `redis`: 缓存视觉分析结果

## 📝 下一步

1. 实现核心工具函数
2. 设计数据库表结构
3. 编写 Agent Prompt
4. 测试典型场景
5. 优化性能（缓存、并行）
