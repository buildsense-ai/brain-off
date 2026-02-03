#!/usr/bin/env python3
"""
实验2: 读取 DXF 文件

学习目标：
1. 使用 ezdxf 库读取 DXF 文件
2. 理解 CAD 文件的基本结构
3. 提取图层、实体信息

安装依赖：
pip install ezdxf
"""

import sys
import os


def check_file_type(file_path):
    """
    检测文件类型：DWG 或 DXF
    """
    if file_path.lower().endswith('.dwg'):
        return 'dwg'
    elif file_path.lower().endswith('.dxf'):
        return 'dxf'
    else:
        return 'unknown'


def prompt_dwg_conversion(dwg_path):
    """
    提示用户转换 DWG 文件
    """
    base_path = dwg_path.rsplit('.', 1)[0]
    dxf_path = base_path + '.dxf'

    print("⚠️  检测到 DWG 文件")
    print("   DWG 是专有格式，需要先转换为 DXF\n")

    # 检查是否已有对应的 DXF 文件
    if os.path.exists(dxf_path):
        print(f"✅ 找到对应的 DXF 文件: {dxf_path}")
        print(f"   将读取 DXF 文件...\n")
        return dxf_path

    print("=" * 60)
    print("📋 推荐的免费在线转换服务（无需注册）")
    print("=" * 60)

    print("\n【推荐1】MiConv")
    print("   网址: https://miconv.com")
    print("   特点: 完全免费，无需注册，2小时后自动删除")

    print("\n【推荐2】GroupDocs")
    print("   网址: https://products.groupdocs.app/conversion/dwg-to-dxf")
    print("   特点: 免费 CAD 转换器，即时下载")

    print("\n【推荐3】AutoDWG")
    print("   网址: https://www.autodwg.com/online-dwg-to-dxf-converter/")
    print("   特点: 支持 AutoCAD R14-2026")

    print("\n" + "=" * 60)
    print("💡 转换步骤")
    print("=" * 60)
    print("1. 访问上述任一网站")
    print("2. 上传你的 DWG 文件")
    print("3. 选择输出格式: DXF")
    print("4. 下载转换后的文件")
    print(f"5. 保存为: {dxf_path}")
    print(f"6. 重新运行: python 02_read_cad.py \"{dxf_path}\"")
    print()

    return None


def read_dxf_basic(file_path):
    """
    基础读取：获取文件元信息

    原理：
    - DXF 文件包含多个 SECTION（段）
    - HEADER: 文件头信息（版本、单位等）
    - TABLES: 图层、线型等定义
    - ENTITIES: 实体数据（线、圆、文字等）
    """
    try:
        import ezdxf
    except ImportError:
        print("❌ 未安装 ezdxf 库")
        print("   请运行: pip install ezdxf")
        return

    try:
        # 读取 DXF 文件
        doc = ezdxf.readfile(file_path)

        print("✅ 文件读取成功！\n")

        # 1. 基本信息
        print("=" * 60)
        print("📋 文件基本信息")
        print("=" * 60)
        print(f"DXF 版本: {doc.dxfversion}")
        print(f"单位: {doc.units}")

        # 2. 图层信息
        print("\n" + "=" * 60)
        print("📐 图层列表")
        print("=" * 60)

        layers = doc.layers
        print(f"图层总数: {len(layers)}")

        for layer in layers:
            print(f"  - {layer.dxf.name} (颜色: {layer.dxf.color})")

        # 3. 实体统计
        print("\n" + "=" * 60)
        print("📊 实体统计")
        print("=" * 60)

        msp = doc.modelspace()
        entity_types = {}

        for entity in msp:
            entity_type = entity.dxftype()
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

        print(f"实体总数: {len(msp)}")
        for entity_type, count in sorted(entity_types.items()):
            print(f"  - {entity_type}: {count}")

        return doc

    except Exception as e:
        print(f"❌ 读取失败: {str(e)}")
        return None


def main():
    print("🔍 CAD 文件读取实验\n")

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        print("用法: python 02_read_cad.py <CAD文件路径>")
        print("\n示例:")
        print("  python 02_read_cad.py building.dxf")
        print("  python 02_read_cad.py building.dwg  # 会提示转换")
        return

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return

    # 检测文件类型
    file_type = check_file_type(file_path)

    if file_type == 'dwg':
        # DWG 文件，提示转换
        dxf_path = prompt_dwg_conversion(file_path)
        if dxf_path:
            # 找到对应的 DXF，读取它
            file_path = dxf_path
        else:
            # 没有 DXF，退出
            return
    elif file_type == 'dxf':
        # DXF 文件，直接读取
        pass
    else:
        print(f"❌ 不支持的文件格式: {file_path}")
        print("   支持的格式: .dxf, .dwg")
        return

    # 读取 DXF 文件
    doc = read_dxf_basic(file_path)

    if doc:
        print("\n✅ 实验成功！")
        print("   下一步: 运行 03_cad_to_image.py 将CAD转为图片")


if __name__ == "__main__":
    main()
