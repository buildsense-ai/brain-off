# 🧪 快速开始指南

## 📋 实验顺序

### 第1步：检查文件格式
```bash
python 01_dwg_to_dxf.py your_file.dwg
```

**学习内容**：
- DWG vs DXF 的区别
- 如何检测文件格式
- 如何转换 DWG 到 DXF

---

### 第2步：读取CAD文件
```bash
python 02_read_cad.py your_file.dxf
```

**学习内容**：
- ezdxf 库的基本使用
- CAD 文件结构（图层、实体）
- 如何统计实体数量

---

### 第3步：CAD转图片
```bash
python 03_cad_to_image.py your_file.dxf
```

**学习内容**：
- matplotlib 渲染 CAD
- 如何生成高清图片
- 为视觉分析准备输入

---

### 第4步：视觉分析（核心）
```bash
python 04_vision_analysis.py your_file.png
```

**学习内容**：
- OpenAI SDK 使用
- base64 编码原理
- 如何调用 Kimi 2.5 视觉模型

---

## ⚙️ 配置步骤

### 1. 安装依赖
```bash
pip install ezdxf matplotlib openai python-dotenv
```

### 2. 配置 API Key
编辑 `../env` 文件：
```bash
VISION_MODEL_API_KEY=your_kimi_api_key_here
```

---

## 💡 实验建议

1. **先用简单的DXF文件测试**（如果没有，可以用AutoCAD创建一个简单的矩形）
2. **每个实验都有详细注释**，慢慢看代码理解原理
3. **遇到问题随时问我**，我会解释具体实现

---

## 🎯 下一步

完成这4个实验后，你就理解了核心原理，可以：
- 修改代码适应你的需求
- 组合这些模块构建完整流程
- 添加更多功能（如工程量计算）
