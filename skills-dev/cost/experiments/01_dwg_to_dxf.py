#!/usr/bin/env python3
"""
实验1: DWG 转 DXF 格式

问题：为什么需要转换？
- DWG 是 AutoCAD 的专有二进制格式，需要 AutoCAD 或专门工具才能读取
- DXF 是开放的文本格式，Python 的 ezdxf 库可以直接读取

转换方法：
1. 使用 ODA File Converter (免费，官方推荐)
2. 使用在线转换工具
3. 使用 AutoCAD 另存为

本实验演示如何检测文件格式并提示转换。
"""

import os
import sys


def check_file_format(file_path):
    """
    检测CAD文件格式

    原理：
    - DWG 文件开头是 "AC1027" 等版本标识（二进制）
    - DXF 文件开头是 "0\nSECTION" （文本）
    """
    if not os.path.exists(file_path):
        return None, "文件不存在"

    try:
        # 读取文件前几个字节
        with open(file_path, 'rb') as f:
            header = f.read(6)

        # 检查是否是 DWG
        if header.startswith(b'AC'):
            version = header.decode('ascii', errors='ignore')
            return 'DWG', f"AutoCAD DWG 格式 (版本: {version})"

        # 检查是否是 DXF
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            if first_line == '0':
                return 'DXF', "AutoCAD DXF 格式"

        return 'UNKNOWN', "未知格式"

    except Exception as e:
        return None, f"读取失败: {str(e)}"


def convert_dwg_to_dxf_guide(dwg_path):
    """
    提供 DWG 转 DXF 的指导

    注意：Python 无法直接转换 DWG，需要外部工具
    """
    print("\n" + "="*60)
    print("📋 DWG 转 DXF 转换指南")
    print("="*60)

    print("\n方法1: 使用 ODA File Converter (推荐)")
    print("  1. 下载: https://www.opendesign.com/guestfiles/oda_file_converter")
    print("  2. 安装后运行")
    print("  3. 选择输入文件夹和输出文件夹")
    print("  4. 选择输出格式: DXF")
    print("  5. 点击转换")

    print("\n方法2: 使用 AutoCAD")
    print("  1. 打开 DWG 文件")
    print("  2. 文件 -> 另存为")
    print("  3. 选择格式: AutoCAD DXF")

    print("\n方法3: 在线转换")
    print("  - https://www.zamzar.com/convert/dwg-to-dxf/")
    print("  - https://convertio.co/zh/dwg-dxf/")

    print("\n转换后，使用 DXF 文件继续后续实验。")
    print("="*60)


def main():
    """主函数"""
    print("🔍 CAD 文件格式检测工具\n")

    # 示例：检测文件
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        print("用法: python 01_dwg_to_dxf.py <CAD文件路径>")
        print("\n示例:")
        print("  python 01_dwg_to_dxf.py building.dwg")
        print("  python 01_dwg_to_dxf.py building.dxf")
        return

    # 检测格式
    format_type, message = check_file_format(file_path)

    print(f"文件: {file_path}")
    print(f"格式: {message}\n")

    if format_type == 'DWG':
        print("⚠️  检测到 DWG 格式，需要转换为 DXF")
        convert_dwg_to_dxf_guide(file_path)

    elif format_type == 'DXF':
        print("✅ DXF 格式，可以直接使用 ezdxf 读取")
        print("   下一步: 运行 02_read_cad.py")

    else:
        print("❌ 无法识别的文件格式")


if __name__ == "__main__":
    main()
