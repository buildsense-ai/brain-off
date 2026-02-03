#!/usr/bin/env python3
"""
DWG 转换辅助工具

由于 API 不支持 DWG 转换，这个脚本帮助你：
1. 检测 DWG 文件信息
2. 提供转换建议
3. 等待你手动转换后，自动进入下一步
"""

import sys
import os
import time


def detect_dwg_info(dwg_path):
    """检测 DWG 文件信息"""
    print("📋 DWG 文件信息：")
    print(f"   路径: {dwg_path}")

    file_size = os.path.getsize(dwg_path)
    print(f"   大小: {file_size / 1024 / 1024:.2f} MB")

    # 读取版本信息
    with open(dwg_path, 'rb') as f:
        header = f.read(6)
        version = header.decode('ascii', errors='ignore')
        print(f"   版本: {version}")

    return version


def suggest_conversion_methods():
    """建议转换方法"""
    print("\n" + "="*60)
    print("🔧 转换方法建议：")
    print("="*60)

    print("\n【方法1】在线转换（最快）")
    print("   1. 打开: https://www.zamzar.com/convert/dwg-to-dxf/")
    print("   2. 上传你的 DWG 文件")
    print("   3. 下载转换后的 DXF 文件")
    print("   4. 保存到同一目录")

    print("\n【方法2】导出为图片（推荐用于视觉分析）")
    print("   如果你有 AutoCAD 或 CAD 查看器：")
    print("   1. 打开 DWG 文件")
    print("   2. 导出为 PNG/PDF")
    print("   3. 保存到同一目录")

    print("\n【方法3】ODA File Converter（批量转换）")
    print("   1. 下载: https://www.opendesign.com/guestfiles/oda_file_converter")
    print("   2. 安装后批量转换")


def wait_for_conversion(dwg_path):
    """等待用户完成转换"""
    base_path = dwg_path.rsplit('.', 1)[0]

    print("\n" + "="*60)
    print("⏳ 等待转换完成...")
    print("="*60)
    print(f"\n请将转换后的文件保存为：")
    print(f"   DXF: {base_path}.dxf")
    print(f"   或")
    print(f"   PNG: {base_path}.png")
    print(f"\n完成后按 Enter 继续，或输入 'skip' 跳过")

    input("\n按 Enter 继续...")

    # 检查转换结果
    dxf_path = base_path + '.dxf'
    png_path = base_path + '.png'
    pdf_path = base_path + '.pdf'

    if os.path.exists(dxf_path):
        print(f"\n✅ 找到 DXF 文件: {dxf_path}")
        print(f"\n下一步: 运行实验2读取 DXF")
        print(f"   python 02_read_cad.py \"{dxf_path}\"")
        return dxf_path, 'dxf'

    elif os.path.exists(png_path):
        print(f"\n✅ 找到 PNG 文件: {png_path}")
        print(f"\n下一步: 运行实验4视觉分析")
        print(f"   python 04_vision_analysis.py \"{png_path}\"")
        return png_path, 'png'

    elif os.path.exists(pdf_path):
        print(f"\n✅ 找到 PDF 文件: {pdf_path}")
        print(f"\n下一步: 运行实验4视觉分析")
        print(f"   python 04_vision_analysis.py \"{pdf_path}\"")
        return pdf_path, 'pdf'

    else:
        print("\n⚠️  未找到转换后的文件")
        print("   请确保文件保存在同一目录下")
        return None, None


def main():
    if len(sys.argv) < 2:
        print("用法: python 01b_manual_conversion_helper.py <DWG文件路径>")
        return

    dwg_path = sys.argv[1]

    if not os.path.exists(dwg_path):
        print(f"❌ 文件不存在: {dwg_path}")
        return

    print("\n" + "="*60)
    print("🔍 DWG 转换辅助工具")
    print("="*60 + "\n")

    # 检测文件信息
    detect_dwg_info(dwg_path)

    # 建议转换方法
    suggest_conversion_methods()

    # 等待转换
    result_path, file_type = wait_for_conversion(dwg_path)

    if result_path:
        print(f"\n🎉 准备就绪！可以继续实验了")


if __name__ == "__main__":
    main()
