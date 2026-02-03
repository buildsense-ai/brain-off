# 为什么 DXF 文件比 DWG 大很多？

## 你的观察

DXF 文件：16 MB
DWG 文件：通常 2-5 MB（同样内容）

**DXF 可能是 DWG 的 3-10 倍大小！**

---

## 核心原因

### 1. 文本格式 vs 二进制格式

**DXF（Drawing Exchange Format）**：
```
# DXF 是文本格式（ASCII）
0
SECTION
2
HEADER
9
$ACADVER
1
AC1015
...
```

**DWG（Drawing）**：
```
# DWG 是二进制格式
AC1015 [二进制数据] ...
```

**对比**：
- 文本格式：每个数字/字符都用 ASCII 编码
- 二进制格式：直接存储二进制数据
- 二进制通常比文本小 3-5 倍

