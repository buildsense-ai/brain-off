# DWG 文件转换指南

## 问题
Convertio API 不支持 DWG 格式的转换（无论是 DWG→DXF 还是 DWG→PNG）

## 解决方案

### 方案1：ODA File Converter（推荐）

**下载地址**：https://www.opendesign.com/guestfiles/oda_file_converter

**特点**：
- ✅ 免费官方工具
- ✅ 支持 DWG ↔ DXF 互转
- ✅ 支持批量转换
- ✅ 支持所有 AutoCAD 版本

**使用步骤**：
1. 下载并安装 ODA File Converter
2. 打开软件
3. 添加你的 DWG 文件
4. 选择输出格式：DXF
5. 选择输出版本：R2013 或更新（ezdxf 支持）
6. 点击转换

**命令行使用**（安装后）：
```bash
# macOS 路径可能是：
/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter \
  "输入文件夹" "输出文件夹" "ACAD2013" "DXF" "0" "1"
```

---

### 方案2：在线手动转换

**网站**：
- https://www.zamzar.com/ （支持 DWG→DXF）
- https://cloudconvert.com/ （支持 DWG→DXF）
- https://www.online-convert.com/ （支持 DWG→DXF）

**步骤**：
1. 上传 DWG 文件
2. 选择输出格式 DXF
3. 下载转换后的文件

---

### 方案3：跳过 DXF，直接分析（推荐用于快速测试）

如果你有 AutoCAD 或其他 CAD 软件：
