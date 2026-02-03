#!/usr/bin/env python3
"""
使用 Convertio API 自动转换 DWG 到 DXF

API Key: c2900251fdb9ebc7bc8937490b3e1c69
文档: https://convertio.co/api/docs/
"""

import sys
import os
import time
import requests


def convert_with_convertio(dwg_path, api_key):
    """使用 Convertio API 自动转换"""

    print("🌐 使用 Convertio API 转换...")

    base_url = "https://api.convertio.co"

    # 步骤1: 上传文件
    print("\n⏳ 步骤1: 上传文件...")

    with open(dwg_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{base_url}/convert",
            data={'apikey': api_key, 'outputformat': 'dxf'},
            files=files
        )

    if response.status_code != 200:
        print(f"❌ 上传失败: {response.text}")
        return None

    result = response.json()

    if result['status'] != 'ok':
        print(f"❌ 错误: {result}")
        return None

    conversion_id = result['data']['id']
    print(f"✅ 上传成功！转换ID: {conversion_id}")

    # 步骤2: 等待转换完成
    print("\n⏳ 步骤2: 等待转换...")

    while True:
        response = requests.get(f"{base_url}/convert/{conversion_id}/status")
        result = response.json()

        if result['data']['step'] == 'finish':
            print("✅ 转换完成！")
            download_url = result['data']['output']['url']
            break
        elif result['data']['step'] == 'error':
            print(f"❌ 转换失败: {result['data']['error']}")
            return None

        print(f"   进度: {result['data']['step']}...")
        time.sleep(2)

    # 步骤3: 下载文件
    print("\n⏳ 步骤3: 下载DXF文件...")

    output_path = dwg_path.replace('.dwg', '.dxf').replace('.DWG', '.dxf')

    response = requests.get(download_url)
    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"✅ 下载完成: {output_path}")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python auto_convert.py <DWG文件路径>")
        return

    dwg_path = sys.argv[1]
    api_key = "c2900251fdb9ebc7bc8937490b3e1c69"

    dxf_path = convert_with_convertio(dwg_path, api_key)

    if dxf_path:
        print(f"\n🎉 转换成功！")
        print(f"   下一步: python 02_read_cad.py {dxf_path}")


if __name__ == "__main__":
    main()
