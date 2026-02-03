#!/usr/bin/env python3
"""
DWG 转换信息工具 - 只显示信息，不等待输入
"""

import sys
import os


def main():
    if len(sys.argv) < 2:
        print("用法: python 01b_conversion_info.py <DWG文件路径>")
        return

    dwg_path = sys.argv[1]

    if not os.path.exists(dwg_path):
        print(f"❌ 文件不存在: {dwg_path}")
        return

    # 文件信息
    file_size = os.path.getsize(dwg_path)
    with open(dwg_path, 'rb') as f:
        version = f.read(6).decode('ascii', errors='ignore')

    base_path = dwg_path.rsplit('.', 1)[0]

    print("\n" + "="*60)
    print("📋 DWG 文件信息")
    print("="*60)
    print(f"路径: {dwg_path}")
    print(f"大小: {file_size / 1024 / 1024:.2f} MB")
    print(f"版本: {version}")

    print("\n" + "="*60)
    print("❌ 问题：Convertio API 不支持 DWG 转换")
    print("="*60)

    print("\n" + "="*60)
    print("✅ 解决方案")
    print("="*60)

    print("\n【推荐】在线转换（最快）")
    print("   网站: https://www.zamzar.com/convert/dwg-to-dxf/")
    print("   步骤:")
    print("   1. 上传 DWG 文件")
    print("   2. 下载 DXF 文件")
    print(f"   3. 保存为: {base_path}.dxf")

    print("\n【备选】导出图片（用于视觉分析）")
    print("   如果有 CAD 软件:")
    print("   1. 打开 DWG 文件")
    print("   2. 导出为 PNG/PDF")
    print(f"   3. 保存为: {base_path}.png")

    print("\n" + "="*60)
    print("📝 转换完成后的下一步")
    print("="*60)
    print(f"\n如果转换为 DXF:")
    print(f"   python 02_read_cad.py \"{base_path}.dxf\"")
    print(f"\n如果导出为图片:")
    print(f"   python 04_vision_analysis.py \"{base_path}.png\"")
    print()


if __name__ == "__main__":
    main()
