#!/usr/bin/env python3
"""
测试在线 DWG→DXF 转换服务

根据搜索结果，测试以下服务：
1. MiConv (https://miconv.com)
2. GroupDocs (https://groupdocs.app)
3. AutoDWG (https://autodwg.com)
4. CloudConvert (https://cloudconvert.com)
"""

import sys
import os
import requests
import time


def test_cloudconvert_api():
    """
    CloudConvert 有公开 API
    但需要 API key（免费额度：25次/天）
    """
    print("\n" + "="*60)
    print("测试 CloudConvert API")
    print("="*60)
    print("CloudConvert 有公开 API，但需要注册获取 API key")
    print("免费额度：25次/天")
    print("注册地址：https://cloudconvert.com/register")
    print()
    return None


def manual_test_guide(dwg_path):
    """
    提供手动测试指南
    """
    print("\n" + "="*60)
    print("📋 手动测试在线转换服务")
    print("="*60)

    print("\n【测试1】MiConv（推荐）")
    print("   1. 打开：https://miconv.com")
    print("   2. 点击 'Choose Files' 上传 DWG")
    print("   3. 选择输出格式：DXF")
    print("   4. 点击 'Convert'")
    print("   5. 下载转换后的文件")

    print("\n【测试2】GroupDocs")
    print("   1. 打开：https://products.groupdocs.app/conversion/dwg-to-dxf")
    print("   2. 上传 DWG 文件")
    print("   3. 点击 'Convert Now'")
    print("   4. 下载 DXF 文件")

    print("\n【测试3】AutoDWG")
    print("   1. 打开：https://www.autodwg.com/online-dwg-to-dxf-converter/")
    print("   2. 上传 DWG 文件")
    print("   3. 等待转换")
    print("   4. 下载 DXF 文件")


def main():
    if len(sys.argv) < 2:
        print("用法: python test_online_converters.py <DWG文件路径>")
        return

    dwg_path = sys.argv[1]

    if not os.path.exists(dwg_path):
        print(f"❌ 文件不存在: {dwg_path}")
        return

    # 文件信息
    file_size = os.path.getsize(dwg_path)
    print(f"\n📂 文件信息：")
    print(f"   路径: {dwg_path}")
    print(f"   大小: {file_size / 1024 / 1024:.2f} MB")

    # 测试 API
    test_cloudconvert_api()

    # 手动测试指南
    manual_test_guide(dwg_path)

    print("\n" + "="*60)
    print("💡 建议")
    print("="*60)
    print("1. 先试 MiConv（最简单，无需注册）")
    print("2. 如果需要批量转换，考虑注册 CloudConvert API")
    print("3. 转换完成后，运行：")
    print(f"   python 02_read_cad.py \"<转换后的DXF路径>\"")
    print()


if __name__ == "__main__":
    main()
