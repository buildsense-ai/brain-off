#!/usr/bin/env python3
"""
实验3: CAD 转图片

学习目标：
1. 将 DXF 文件渲染为图片
2. 理解 matplotlib 可视化原理
3. 为视觉分析准备输入

安装依赖：
pip install ezdxf matplotlib
"""

import sys
import os


def convert_dxf_to_image(dxf_path, output_path=None, max_size=None, dpi=300, output_format='png'):
    """
    将 DXF 转换为图片（优化版）

    原理：
    - 计算实际图形边界，裁剪空白
    - 自适应调整画布尺寸
    - 支持高 DPI PNG 或矢量 PDF 输出

    参数：
    - max_size: 最大边长（像素），None 表示不限制
    - dpi: 输出分辨率（PNG 推荐 300-600，PDF 推荐 72-150）
    - output_format: 'png' 或 'pdf'
    """
    try:
        import ezdxf
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        import matplotlib.pyplot as plt
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("   请运行: pip install ezdxf matplotlib")
        return None

    try:
        # 1. 读取 DXF
        print("📂 读取 DXF 文件...")
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()

        # 2. 计算实际边界
        print("📐 计算图形边界...")
        try:
            # 方法1: 使用 bbox() 计算边界
            from ezdxf.bbox import extents
            bbox = extents(msp)

            if bbox.has_data:
                # 获取边界框
                min_x, min_y = bbox.extmin.x, bbox.extmin.y
                max_x, max_y = bbox.extmax.x, bbox.extmax.y

                # 计算实际尺寸
                actual_width = max_x - min_x
                actual_height = max_y - min_y

                print(f"   边界: ({min_x:.1f}, {min_y:.1f}) -> ({max_x:.1f}, {max_y:.1f})")
                print(f"   尺寸: {actual_width:.1f} x {actual_height:.1f}")

                # 计算画布比例
                aspect_ratio = actual_width / actual_height if actual_height > 0 else 1.0

                # 根据最大尺寸限制计算画布大小
                if max_size:
                    # 有尺寸限制
                    if aspect_ratio > 1:
                        width = max_size / dpi
                        height = width / aspect_ratio
                    else:
                        height = max_size / dpi
                        width = height * aspect_ratio
                else:
                    # 无限制，按实际尺寸输出（假设 1 单位 = 1mm）
                    # 转换为英寸：mm / 25.4
                    width = actual_width / 25.4 / 10  # 缩小 10 倍避免过大
                    height = actual_height / 25.4 / 10

                print(f"   画布: {width:.1f} x {height:.1f} 英寸")
            else:
                raise ValueError("无边界数据")

        except Exception as e:
            print(f"⚠️  无法计算边界: {e}")
            print("   使用默认设置")
            width, height = 12, 8
            bbox = None
            min_x = min_y = max_x = max_y = None
            actual_width = actual_height = None

        # 3. 创建渲染上下文
        print("🎨 创建渲染上下文...")
        fig = plt.figure(figsize=(width, height))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()  # 隐藏坐标轴

        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)

        # 4. 渲染
        print("🖼️  渲染图形...")
        Frontend(ctx, out).draw_layout(msp, finalize=True)

        # 5. 设置视图边界（裁剪空白）
        if bbox is not None and bbox.has_data:
            margin_x = actual_width * 0.05
            margin_y = actual_height * 0.05
            ax.set_xlim(min_x - margin_x, max_x + margin_x)
            ax.set_ylim(min_y - margin_y, max_y + margin_y)

        # 6. 保存
        if not output_path:
            base_name = os.path.splitext(dxf_path)[0]
            output_path = f"{base_name}.{output_format}"

        print(f"💾 保存图片: {output_path}")
        print(f"   格式: {output_format.upper()}")
        print(f"   分辨率: {dpi} DPI")

        if output_format == 'pdf':
            fig.savefig(output_path, format='pdf', bbox_inches='tight', pad_inches=0.1)
        else:
            fig.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)

        plt.close()

        # 7. 显示文件信息
        file_size = os.path.getsize(output_path) / 1024 / 1024
        print(f"✅ 转换成功！")
        print(f"   图片路径: {output_path}")
        print(f"   文件大小: {file_size:.2f} MB")

        return output_path

    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("🖼️  CAD 转图片实验\n")

    if len(sys.argv) > 1:
        dxf_path = sys.argv[1]
    else:
        print("用法: python 03_cad_to_image.py <DXF文件路径>")
        print("\n示例:")
        print("  python 03_cad_to_image.py building.dxf")
        return

    output_path = convert_dxf_to_image(dxf_path)

    if output_path:
        print("\n✅ 实验成功！")
        print("   下一步: 运行 04_vision_analysis.py 分析图片")


if __name__ == "__main__":
    main()
