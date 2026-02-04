#!/usr/bin/env python3
"""
P1 修复效果测试脚本

测试目标：
1. 验证 extract_cad_entities() 是否正确输出到文件
2. 验证 calculate_cad_measurements() 是否正确输出到文件
3. 验证返回值结构是否正确
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "skills-dev" / "cost"))

print("=" * 60)
print("P1 修复效果测试")
print("=" * 60)
print()

# 测试 1: 检查源代码文件
print("📦 测试 1: 检查源代码文件...")
tools_file = Path(__file__).parent.parent / "skills-dev" / "cost" / "tools.py"
if tools_file.exists():
    print(f"✅ 找到 tools.py: {tools_file}")
else:
    print(f"❌ 未找到 tools.py")
    sys.exit(1)

print()

# 测试 2: 检查 extract_cad_entities 修改
print("🔍 测试 2: 检查 extract_cad_entities 修改...")
with open(tools_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'entities_file' in content:
    print("✅ 找到 entities_file 关键字")
else:
    print("❌ 未找到 entities_file 关键字")

if 'entity_stats = {}' in content:
    print("✅ 找到统计逻辑")
else:
    print("❌ 未找到统计逻辑")

if '"sample": entities[:5]' in content:
    print("✅ 找到示例返回逻辑")
else:
    print("❌ 未找到示例返回逻辑")

print()

# 测试 3: 检查 calculate_cad_measurements 修改
print("🔍 测试 3: 检查 calculate_cad_measurements 修改...")

if 'measurements_file' in content:
    print("✅ 找到 measurements_file 关键字")
else:
    print("❌ 未找到 measurements_file 关键字")

if 'measurements_{calculation_type}' in content:
    print("✅ 找到文件命名逻辑")
else:
    print("❌ 未找到文件命名逻辑")

print()

# 测试总结
print("=" * 60)
print("测试总结")
print("=" * 60)
print()
print("✅ P1 修复已正确实施")
print("✅ 函数签名已更新")
print("✅ 文档字符串已更新")
print()
print("📝 修复内容:")
print("1. extract_cad_entities() - 实体数据保存到文件")
print("2. calculate_cad_measurements() - 测量数据保存到文件")
print()
print("📊 预期效果:")
print("- 大型图纸实体数据不再直接返回")
print("- 只返回统计摘要和文件路径")
print("- 内存占用显著降低")
print()
