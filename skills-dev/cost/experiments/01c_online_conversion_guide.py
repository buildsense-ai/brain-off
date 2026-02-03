#!/usr/bin/env python3
"""
测试免费在线 DWG→DXF 转换服务

根据搜索结果，以下服务支持免费、无需注册的转换：
1. MiConv (https://miconv.com) - 推荐
2. GroupDocs (https://groupdocs.app)
3. AutoDWG (https://autodwg.com)
4. CloudConvert (https://cloudconvert.com)
5. Online-convert.com (https://online-convert.com)
"""

import sys
import os
import requests
import time


def test_cloudconvert(dwg_path):
    """
    测试 CloudConvert API
    注意：CloudConvert 有 API，但需要 API key
    """
    print("⚠️  CloudConvert 需要 API key，跳过")
    return None


def manual_conversion_guide(dwg_path):
    """
    提供手动转换指南
    """
    base_path = dwg_path.rsplit('.', 1)[0]

    print("\n" + "="*60)
    print("📋 免费在线转换服务（无需注册）")
    print("="*60)

    print("\n【推荐1】MiConv")
    print("   网址: https://miconv.com")
    print("   特点: 完全免费，无需注册，2小时后自动删除")
    print("   步骤:")
    print("   1. 打开网站")
    print("   2. 上传你的 DWG 文件")
    print("   3. 选择输出格式: DXF")
    print("   4. 点击转换")
    print(f"   5. 下载并保存为: {base_path}.dxf")

    print("\n【推荐2】GroupDocs")
    print("   网址: https://groupdocs.app")
    print("   特点: 免费 CAD 转换器，即时下载")

    print("\n【推荐3】AutoDWG")
    print("   网址: https://autodwg.com")
    print("   特点: 支持 AutoCAD R14-2026")
    print("   你的文件版本: AC1015 (AutoCAD 2000) ✅ 支持")

    print("\n" + "="*60)
    print("💡 建议")
    print("="*60)
    print("1. 先试 MiConv（最简单）")
    print("2. 如果失败，试 GroupDocs 或 AutoDWG")
    print("3. 转换完成后，运行:")
    print(f"   python 02_read_cad.py \"{base_path}.dxf\"")
    print()


def main():
    if len(sys.argv) < 2:
        print("用法: python 01c_online_conversion_guide.py <DWG文件路径>")
        return

    dwg_path = sys.argv[1]

    if not os.path.exists(dwg_path):
        print(f"❌ 文件不存在: {dwg_path}")
        return

    # 检测文件信息
    file_size = os.path.getsize(dwg_path)
    with open(dwg_path, 'rb') as f:
        version = f.read(6).decode('ascii', errors='ignore')

    print("\n" + "="*60)
    print("📂 DWG 文件信息")
    print("="*60)
    print(f"路径: {dwg_path}")
    print(f"大小: {file_size / 1024 / 1024:.2f} MB")
    print(f"版本: {version}")

    # 提供转换指南
    manual_conversion_guide(dwg_path)


if __name__ == "__main__":
    main()
