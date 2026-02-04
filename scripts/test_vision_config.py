#!/usr/bin/env python3
"""测试 Vision Model 配置"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_env_variables():
    """测试 1: 环境变量配置"""
    print("=" * 60)
    print("测试 1: 环境变量配置")
    print("=" * 60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "VISION_MODEL_API_KEY": os.getenv("VISION_MODEL_API_KEY"),
        "VISION_MODEL_BASE_URL": os.getenv("VISION_MODEL_BASE_URL"),
        "VISION_MODEL_NAME": os.getenv("VISION_MODEL_NAME")
    }
    
    all_set = True
    for var_name, value in required_vars.items():
        has_value = value and "placeholder" not in value.lower()
        status = "✅" if has_value else "❌"
        display_value = value[:20] + "..." if value and len(value) > 20 else value
        print(f"{status} {var_name}: {display_value}")
        if not has_value:
            all_set = False
    
    print(f"\n{'✅ 测试 1 通过' if all_set else '❌ 测试 1 失败'}\n")
    return all_set
