#!/usr/bin/env python3
"""
DWG 自动在线转换工具

使用 Convertio API 自动转换（需要API Key，但有免费额度）
或者提供简化的手动转换指导

安装依赖：
pip install requests
"""

import sys
import os
import requests
import time
from pathlib import Path


def simple_online_guide(dwg_path):
    """
    提供简化的在线转换指导

    由于大多数免费API都需要注册，
    我们提供最简单的手动步骤
    """
    print("\n" + "="*60)
    print("🌐 在线转换指南（最简单）")
    print("="*60)

    print("\n📋 步骤：")
    print("1. 打开浏览器访问: https://convertio.co/zh/dwg-dxf/")
    print("2. 点击「选择文件」按钮")
    print(f"3. 选择你的文件: {dwg_path}")
    print("4. 点击「转换」按钮")
    print("5. 等待转换完成（通常1-2分钟）")
    print("6. 点击「下载」按钮")

    output_name = os.path.basename(dwg_path).replace('.dwg', '.dxf')
    print(f"\n💾 下载后的文件名: {output_name}")
    print(f"   建议保存到: {os.path.dirname(dwg_path)}")

    print("\n✅ 转换完成后，运行:")
    print(f"   python 02_read_cad.py <下载的dxf文件路径>")
    print("="*60)


def main():
    print("🔄 DWG 在线转换工具\n")

    if len(sys.argv) < 2:
        print("用法: python convert_online.py <DWG文件路径>")
        return

    dwg_path = sys.argv[1]

    if not os.path.exists(dwg_path):
        print(f"❌ 文件不存在: {dwg_path}")
        return

    # 提供转换指导
    simple_online_guide(dwg_path)

    print("\n💡 提示：")
    print("   如果你经常需要转换，可以考虑:")
    print("   1. 注册 Convertio 账号（免费10次/天）")
    print("   2. 或者安装 ODA File Converter（本地转换）")


if __name__ == "__main__":
    main()
