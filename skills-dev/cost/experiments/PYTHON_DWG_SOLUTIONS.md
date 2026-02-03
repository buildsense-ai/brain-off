# Python 直接读取 DWG 文件的解决方案

## 核心问题

**能否在 Python 代码层面直接读取 DWG，不需要手动转换？**

---

## 方案对比

### 方案1：GNU LibreDWG（开源，有 Python 绑定）

**项目地址**：
- 官方：https://www.gnu.org/software/libredwg/
- GitHub 镜像：https://github.com/LibreDWG/libredwg

**特点**：
- ✅ 开源（GPL 许可）
- ✅ 有 Python 3 绑定（通过 SWIG 生成）
- ✅ 可以直接读写 DWG 文件
- ✅ 支持 DWG→DXF 转换
- ⚠️ 主要支持 R2010 及以后版本
- ❌ 你的文件是 AC1015（R2000），可能不支持或支持不完整

**安装方式**：
```bash
# 需要从源码编译（不能用 pip install）
git clone https://github.com/LibreDWG/libredwg.git
cd libredwg
sh autogen.sh
./configure --enable-python
make
sudo make install
```

**Python 使用示例**：
```python
import LibreDWG

# 读取 DWG 文件
dwg = LibreDWG.read_dwg("file.dwg")

# 转换为 DXF
LibreDWG.dwg_to_dxf("input.dwg", "output.dxf")
```

**问题**：
- ❌ 安装复杂（需要编译）
- ❌ 你的 AC1015（R2000）版本可能不支持
- ❌ macOS 上可能有兼容性问题

---

### 方案2：Aspose.CAD for Python（商业，功能完整）

**项目地址**：https://products.aspose.com/cad/python-net/

**特点**：
- ✅ 商业库，功能完整
- ✅ 支持最新版本的 DWG
- ✅ 可以直接读取 DWG
- ✅ 支持转换为 PDF、图片等
- ✅ 不需要 AutoCAD
- ❌ 商业授权（付费）

**安装方式**：
```bash
pip install aspose-cad
```

**Python 使用示例**：
```python
import aspose.cad as cad

# 读取 DWG 文件
image = cad.Image.load("file.dwg")

# 转换为 DXF
image.save("output.dxf", cad.imageoptions.DxfOptions())

# 或转换为 PDF
pdf_options = cad.imageoptions.CadRasterizationOptions()
image.save("output.pdf", pdf_options)
```

**问题**：
- ❌ 需要付费（商业授权）
- ⚠️ 可能有免费试用期

---

### 方案3：ODA Platform（商业，最完整）

**项目地址**：https://www.opendesign.com/

**特点**：
- ✅ 功能最完整（接近官方）
- ✅ 支持所有 DWG 版本
- ✅ 有 Python 绑定（通过 SWIG）
- ❌ 商业授权（需要申请）
- ❌ 安装复杂

**问题**：
- ❌ 不是真正的开源
- ❌ 需要商业授权或申请免费许可

---

### 方案4：混合方案（推荐）

**使用 subprocess 调用命令行工具**：

```python
import subprocess
import os

def convert_dwg_to_dxf_with_libredwg(dwg_path):
    """使用 LibreDWG 命令行工具转换"""
    dxf_path = dwg_path.replace('.dwg', '.dxf')

    # 调用 dwg2dxf 命令行工具
    result = subprocess.run(
        ['dwg2dxf', '-o', dxf_path, dwg_path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return dxf_path
    else:
        return None
```

**优势**：
- ✅ 不需要 Python 绑定
- ✅ 可以使用任何命令行工具
- ✅ 灵活性高

**前提**：
- 需要安装 LibreDWG 命令行工具

---

## 实际测试结果

### macOS 上的情况

```bash
# Homebrew 搜索结果
$ brew search libredwg
libre
librecad  # 这是 CAD 软件，不是 LibreDWG

# 命令行工具检查
$ which dwg2dxf
dwg2dxf not found
```

**结论**：
- ❌ Homebrew 没有 LibreDWG
- ❌ 需要手动编译安装（复杂）

---

## 最终推荐方案

### 对于你的项目

**现实情况**：
1. ❌ LibreDWG - 安装复杂，版本支持有限
2. ❌ Aspose.CAD - 商业授权，需要付费
3. ❌ ODA Platform - 商业授权，需要申请
4. ✅ **在线转换 + ezdxf** - 最实用的方案

---

## 实用的混合方案

```python
import os
import ezdxf

def analyze_cad_file(file_path):
    """
    智能处理 CAD 文件
    """
    if file_path.endswith('.dxf'):
        # 直接读取 DXF
        return read_dxf(file_path)

    elif file_path.endswith('.dwg'):
        # 检查是否有对应的 DXF
        dxf_path = file_path.replace('.dwg', '.dxf')

        if os.path.exists(dxf_path):
            print(f"✅ 找到 DXF 文件: {dxf_path}")
            return read_dxf(dxf_path)
        else:
            print(f"⚠️  需要先转换 DWG → DXF")
            print(f"   请访问: https://miconv.com")
            print(f"   转换后保存为: {dxf_path}")
            return None

def read_dxf(dxf_path):
    """读取 DXF 文件"""
    doc = ezdxf.readfile(dxf_path)
    return doc
```

---

## 总结

### 回答你的问题

**"有没有能够 access DWG 文件的 Python package？"**

**开源方案**：
- LibreDWG - 有 Python 绑定，但安装复杂，版本支持有限

**商业方案**：
- Aspose.CAD - 功能完整，但需要付费
- ODA Platform - 最完整，但需要商业授权

**现实建议**：
- ✅ 使用在线转换服务（MiConv、GroupDocs、AutoDWG）
- ✅ 转换后用 ezdxf 处理
- ✅ 在代码中检测 DXF 是否存在，提示用户转换

---

## 下一步

1. **短期方案**：使用在线转换
   - 访问 https://miconv.com
   - 上传你的 DWG 文件
   - 下载 DXF 文件

2. **长期方案**：如果需要批量处理
   - 考虑购买 Aspose.CAD 授权
   - 或者申请 ODA 免费许可

3. **继续实验**：
   - 转换完成后运行 `02_read_cad.py`
   - 测试 ezdxf 读取和计算功能
