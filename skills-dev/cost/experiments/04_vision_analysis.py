#!/usr/bin/env python3
"""
实验4: 视觉分析 - 使用 Kimi 2.5 分析图纸

学习目标：
1. 理解 OpenAI SDK 的使用
2. 学习如何发送图片给多模态模型
3. 理解 base64 编码原理

安装依赖：
pip install openai python-dotenv

配置：
在 cost/.env 文件中设置：
VISION_MODEL_BASE_URL=https://api.moonshot.cn/v1
VISION_MODEL_API_KEY=your_kimi_api_key
VISION_MODEL_NAME=moonshot-v1-vision
"""

import sys
import os
import base64
from pathlib import Path


def load_env():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        # 从 cost 目录加载 .env
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        return True
    except ImportError:
        print("❌ 未安装 python-dotenv")
        print("   请运行: pip install python-dotenv")
        return False


def analyze_image_with_vision(image_path, question="请描述这张图纸的内容"):
    """
    使用视觉模型分析图片

    原理：
    1. 读取图片文件
    2. 转换为 base64 编码（文本格式）
    3. 通过 API 发送给模型
    4. 接收模型的文字描述
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ 未安装 openai 库")
        print("   请运行: pip install openai")
        return None

    # 1. 检查环境变量
    api_key = os.getenv("VISION_MODEL_API_KEY")
    base_url = os.getenv("VISION_MODEL_BASE_URL", "https://api.moonshot.cn/v1")
    model_name = os.getenv("VISION_MODEL_NAME", "moonshot-v1-vision")

    if not api_key:
        print("❌ 未配置 API Key")
        print("   请在 cost/.env 文件中设置 VISION_MODEL_API_KEY")
        return None

    print(f"🔧 配置信息:")
    print(f"   API URL: {base_url}")
    print(f"   模型: {model_name}")
    print()

    # 2. 读取图片并转为 base64
    print(f"📂 读取图片: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        print(f"✅ 图片已编码 (大小: {len(image_data)} 字符)")
    except Exception as e:
        print(f"❌ 读取图片失败: {e}")
        return None

    # 3. 创建客户端
    print(f"\n🤖 连接到视觉模型...")
    client = OpenAI(base_url=base_url, api_key=api_key)

    # 4. 发送请求
    print(f"💬 提问: {question}")
    print(f"⏳ 等待模型响应...\n")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.3,
        )

        # 5. 获取结果
        result = response.choices[0].message.content

        print("=" * 60)
        print("🎯 分析结果:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        return result

    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        return None


def main():
    print("👁️  视觉分析实验\n")

    # 加载环境变量
    if not load_env():
        return

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("用法: python 04_vision_analysis.py <图片路径>")
        print("\n示例:")
        print("  python 04_vision_analysis.py building.png")
        return

    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return

    # 分析图片
    result = analyze_image_with_vision(image_path)

    if result:
        print("\n✅ 实验成功！")
        print("   你已经学会了如何使用视觉模型分析图纸")


if __name__ == "__main__":
    main()
