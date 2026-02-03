# 临时工作空间

用于 CAD 算量实验的临时文件管理

## 目录结构

```
temp_workspace/
├── input/          # 输入文件
│   ├── 甲类仓库建施.dxf    # 原始 DXF 文件
│   └── 甲类仓库建施.pdf    # PDF 矢量图
├── output/         # 输出文件
│   ├── images/     # 生成的图片
│   └── data/       # 提取的数据（JSON/CSV）
└── analysis/       # 分析结果
    ├── vision/     # 视觉分析报告
    └── code/       # 代码分析结果

## 工作流程

1. **输入** - 将测试文件放入 input/
2. **处理** - 运行实验脚本
3. **输出** - 结果保存到 output/
4. **分析** - 分析报告保存到 analysis/
