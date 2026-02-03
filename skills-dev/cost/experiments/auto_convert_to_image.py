#!/usr/bin/env python3
"""
使用 Convertio API 将 DWG 转换为 PNG 图像
这样可以直接用视觉模型分析，跳过 DXF 步骤

API Key: c2900251fdb9ebc7bc8937490b3e1c69
"""

import sys
import os
import time
import requests


def convert_dwg_to_image(dwg_path, api_key, output_format="png"):
    """使用Convertio API转换DWG到图像格式"""

    print(f"🌐 使用 Convertio API 转换 DWG → {output_format.upper()}...\n")

    base_url = "https://api.convertio.co"
    filename = os.path.basename(dwg_path)

    # 步骤1: 启动转换任务
    print("⏳ 步骤1: 启动转换任务...")

    response = requests.post(
        f"{base_url}/convert",
        json={
            "apikey": api_key,
            "input": "upload",
            "outputformat": output_format
        }
    )

    if response.status_code != 200:
        print(f"❌ 启动失败: {response.text}")
        return None

    result = response.json()
    if result['status'] != 'ok':
        print(f"❌ 错误: {result}")
        return None

    conversion_id = result['data']['id']
    print(f"✅ 任务创建成功！ID: {conversion_id}")

    # 步骤2: 上传文件
    print(f"\n⏳ 步骤2: 上传文件 {filename}...")

    with open(dwg_path, 'rb') as f:
        response = requests.put(
            f"{base_url}/convert/{conversion_id}/{filename}",
            data=f
        )

    if response.status_code != 200:
        print(f"❌ 上传失败: {response.text}")
        return None

    print("✅ 文件上传成功！")

    # 步骤3: 等待转换完成
    print("\n⏳ 步骤3: 等待转换...")

    max_wait = 120  # 最多等待2分钟
    start_time = time.time()

    while time.time() - start_time < max_wait:
        response = requests.get(f"{base_url}/convert/{conversion_id}/status")
        result = response.json()

        if result['status'] != 'ok':
            print(f"❌ 状态查询失败: {result}")
            return None

        step = result['data']['step']
        print(f"   当前状态: {step}")

        if step == 'finish':
            print("✅ 转换完成！")
            download_url = result['data']['output']['url']
            break
        elif step == 'error':
            error_msg = result['data'].get('error', '未知错误')
            print(f"❌ 转换失败: {error_msg}")
            return None

        time.sleep(3)
    else:
        print("❌ 转换超时")
        return None

    # 步骤4: 下载文件
    print(f"\n⏳ 步骤4: 下载{output_format.upper()}文件...")

    output_path = dwg_path.rsplit('.', 1)[0] + f'.{output_format}'

    response = requests.get(download_url)
    with open(output_path, 'wb') as f:
        f.write(response.content)

    file_size = os.path.getsize(output_path)
    print(f"✅ 下载完成: {output_path}")
    print(f"   文件大小: {file_size / 1024:.1f} KB")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python auto_convert_to_image.py <DWG文件路径> [格式]")
        print("格式: png (默认), pdf, jpg")
        return

    dwg_path = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "png"

    if not os.path.exists(dwg_path):
        print(f"❌ 文件不存在: {dwg_path}")
        return

    api_key = "c2900251fdb9ebc7bc8937490b3e1c69"

    print(f"📂 输入文件: {dwg_path}")
    print(f"🎯 目标格式: {output_format.upper()}\n")

    image_path = convert_dwg_to_image(dwg_path, api_key, output_format)

    if image_path:
        print(f"\n🎉 转换成功！")
        print(f"\n下一步: 运行实验4进行视觉分析")
        print(f"   python 04_vision_analysis.py \"{image_path}\"")


if __name__ == "__main__":
    main()
