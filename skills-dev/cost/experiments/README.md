# 实验测试环境

这个文件夹用于单独测试每个模块，逐步理解实现原理。

## 📂 实验模块

### 1. DWG/DXF 转换测试
- `01_dwg_to_dxf.py` - DWG转DXF格式
- 说明：DWG是AutoCAD专有格式，需要先转换

### 2. CAD文件读取测试
- `02_read_cad.py` - 使用ezdxf读取DXF文件
- 学习：如何提取图层、实体、坐标

### 3. CAD转图片测试
- `03_cad_to_image.py` - 将CAD渲染为图片
- 学习：matplotlib可视化

### 4. 视觉分析测试
- `04_vision_analysis.py` - 使用Kimi分析图片
- 学习：OpenAI SDK调用

### 5. 工程量计算测试
- `05_calculate_quantity.py` - 计算长度、面积
- 学习：几何计算逻辑

### 6. 数据库操作测试
- `06_database_test.py` - 测试增删改查
- 学习：SQLAlchemy使用

## 🚀 使用方法

每个文件都是独立的，可以单独运行：
```bash
cd experiments
python 01_dwg_to_dxf.py
```

每个文件都有详细注释，解释实现原理。
