#!/usr/bin/env python3
"""
实验1增强版: DWG 自动转换为 DXF

支持多种转换方式：
1. 使用 ODA File Converter (需要预先安装)
2. 使用 LibreDWG (开源，pip安装)
3. 提供在线转换指导

安装 LibreDWG (可选):
brew install libredwg  # macOS
apt-get install libredwg  # Linux
"""

import sys
import os
import subprocess
from pathlib import Path


def try_libredwg_convert(dwg_path, output_path=None):
    """
    尝试使用 LibreDWG 转换

    LibreDWG 是开源的 DWG 读取库
    优点：免费、开源
    缺点：支持的版本有限，可能失败
    """
    if not output_path:
        output_path = dwg_path.replace('.dwg', '.dxf').replace('.DWG', '.dxf')

    print("🔄 尝试使用 LibreDWG 转换...")

    # 检查是否安装了 dwg2dxf 命令
    try:
        result = subprocess.run(['which', 'dwg2dxf'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ 未安装 LibreDWG")
            print("   macOS: brew install libredwg")
            print("   Linux: apt-get install libredwg")
            return None
    except Exception:
        return None

    # 执行转换
    try:
        print(f"   输入: {dwg_path}")
        print(f"   输出: {output_path}")

        result = subprocess.run(
            ['dwg2dxf', '-o', output_path, dwg_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✅ 转换成功！")
            print(f"   DXF文件: {output_path}")
            return output_path
        else:
            print(f"❌ 转换失败: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print("❌ 转换超时")
        return None
    except Exception as e:
        print(f"❌ 转换出错: {e}")
        return None


def try_oda_converter(dwg_path, output_path=None):
    """
    尝试使用 ODA File Converter

    需要预先安装 ODA File Converter
    macOS 默认安装路径: /Applications/ODAFileConverter.app
    """
    print("🔄 尝试使用 ODA File Converter...")

    # macOS 路径
    oda_path = "/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"

    if not os.path.exists(oda_path):
        print("❌ 未安装 ODA File Converter")
        print("   下载: https://www.opendesign.com/guestfiles/oda_file_converter")
        return None

    print("⚠️  ODA File Converter 需要图形界面，无法命令行调用")
    print("   请手动打开 ODA File Converter 进行转换")
    return None


def provide_online_conversion_guide(dwg_path):
    """提供在线转换指导"""
    print("\n" + "="*60)
    print("🌐 在线转换方案（最简单）")
    print("="*60)

    print("\n推荐网站：")
    print("1. Convertio (支持大文件)")
    print("   https://convertio.co/zh/dwg-dxf/")
    print("   - 上传你的 DWG 文件")
    print("   - 选择转换为 DXF")
    print("   - 下载转换后的文件")

    print("\n2. Zamzar")
    print("   https://www.zamzar.com/convert/dwg-to-dxf/")

    print("\n3. CloudConvert")
    print("   https://cloudconvert.com/dwg-to-dxf")

    print("\n" + "="*60)
    print("💡 转换后，运行:")
    print(f"   python 02_read_cad.py <转换后的dxf文件>")
    print("="*60)


def main():
    print("🔄 DWG 自动转换工具\n")

    if len(sys.argv) < 2:
        print("用法: python 01_dwg_to_dxf_auto.py <DWG文件路径>")
        return

    dwg_path = sys.argv[1]

    if not os.path.exists(dwg_path):
        print(f"❌ 文件不存在: {dwg_path}")
        return

    print(f"📂 文件: {dwg_path}\n")

    # 尝试方法1: LibreDWG
    dxf_path = try_libredwg_convert(dwg_path)

    if dxf_path:
        print("\n✅ 转换成功！可以继续下一步:")
        print(f"   python 02_read_cad.py {dxf_path}")
        return

    # 尝试方法2: ODA Converter
    print()
    try_oda_converter(dwg_path)

    # 方法3: 在线转换指导
    provide_online_conversion_guide(dwg_path)


if __name__ == "__main__":
    main()
