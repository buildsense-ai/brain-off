# 工程造价 Agent

## 📋 Skill 信息

- **ID**: `cost`
- **名称**: 工程造价智能助手
- **版本**: 0.1.0
- **状态**: ✅ 核心功能已完成

## 🎯 功能描述

基于CAD图纸的智能工程量清单生成系统，支持：
- 📐 CAD图纸分析（DXF/DWG）
- 👁️ 多模态视觉理解
- 📊 自动工程量计算
- 💰 定额查询与匹配
- 📝 工程量清单编制
- 📤 Excel报表导出

## 🚀 两种运行方式

### 方式1：独立CLI运行 ⭐（推荐快速测试）

```bash
# 进入目录
cd skills-dev/cost

# 启动独立Agent
./run.sh

# 或直接运行
python3 cost_agent.py
```

**交互示例**：
```
> load /path/to/building.dxf    # 加载CAD文件
> analyze                        # 分析图纸
> status                         # 查看进度
> export                         # 导出Excel
> quit                           # 退出
```

### 方式2：作为Skill集成到主系统

```bash
# 在主系统中
cd ../../
python chat.py

# 用户输入
> 帮我分析这个CAD图纸，生成工程量清单
```

系统会自动调用 cost skill 的工具。

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `ezdxf` - CAD文件读取
- `openai` - 视觉分析（兼容Kimi 2.5）
- `openpyxl` - Excel导出
- `sqlalchemy` - 数据库ORM
- `psycopg2-binary` - PostgreSQL驱动

## ⚙️ 配置

### 1. 环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```bash
# 视觉模型配置（必需）
VISION_MODEL_BASE_URL=https://api.moonshot.cn/v1
VISION_MODEL_API_KEY=your_kimi_api_key_here
VISION_MODEL_NAME=moonshot-v1-vision

# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/cost_db

# 导出目录
EXPORT_DIR=./exports
```

### 2. 初始化数据库

```bash
# 在项目根目录
python scripts/init_db.py
```

会创建以下表：
- `cost_cad_files` - CAD文件管理
- `cost_analysis_plans` - 分析计划
- `cost_plan_notes` - 分析笔记
- `cost_boq_items` - 工程量清单
- `cost_visual_analyses` - 视觉分析缓存
- `cost_quota_standards` - 定额数据库

## 🛠️ 核心工具（21个）

### CAD数据工具
- `load_cad_file` - 加载CAD文件
- `extract_cad_entities` - 提取实体
- `calculate_cad_measurements` - 计算工程量

### 视觉理解工具
- `convert_cad_to_image` - CAD转图片
- `analyze_drawing_visual` - AI分析图纸
- `extract_drawing_annotations` - 提取标注

### 计划管理工具
- `create_analysis_plan` - 创建计划
- `update_plan_progress` - 更新进度
- `get_plan_context` - 获取上下文
- `add_plan_note` - 添加笔记

### 清单编辑工具
- `create_boq_item` - 创建清单项
- `update_boq_item` - 更新清单项
- `query_boq` - 查询清单
- `calculate_boq_total` - 计算总价

### 定额检索工具
- `search_quota_standard` - 搜索定额
- `add_quota_to_database` - 添加定额
- `update_quota_from_search` - 增量更新

### 导出工具
- `export_boq_to_excel` - 导出Excel

## 📊 数据模型

详见 [models.py](models.py)，包含5张核心表：
- `CADFile` - CAD文件管理
- `AnalysisPlan` - 分析计划（工作记忆）
- `PlanNote` - 分析笔记（决策追踪）
- `BOQItem` - 工程量清单
- `VisualAnalysis` - 视觉分析缓存
