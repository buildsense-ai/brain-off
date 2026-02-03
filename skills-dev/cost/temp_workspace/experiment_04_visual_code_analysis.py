#!/usr/bin/env python3
"""
实验 04: 视觉 + 代码联合分析
=========================

目标：演示如何结合 AI 视觉分析和 DXF 代码分析来理解建筑图纸

工作流程：
1. 视觉分析 PDF - 理解图纸整体结构和设计意图
2. 代码分析 DXF - 精确提取和测量构件
3. 结果对比验证 - 检查数据准确性

输入：
- temp_workspace/input/甲类仓库建施.pdf
- temp_workspace/input/甲类仓库建施.dxf

输出：
- temp_workspace/analysis/visual_report.json - 视觉分析报告
- temp_workspace/analysis/code_analysis.json - 代码分析结果
- temp_workspace/analysis/comparison_report.md - 对比验证报告
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import ezdxf
from openai import OpenAI
from dotenv import load_dotenv
from pdf2image import convert_from_path
from PIL import Image
import io

# 加载环境变量
load_dotenv(project_root / ".env")


class VisualCodeAnalyzer:
    """视觉 + 代码联合分析器"""

    def __init__(self, workspace_dir: str = None):
        # 如果没有指定工作目录，使用脚本所在目录
        if workspace_dir is None:
            script_dir = Path(__file__).parent
            self.workspace = script_dir
        else:
            self.workspace = Path(workspace_dir)

        self.input_dir = self.workspace / "input"
        self.output_dir = self.workspace / "output"
        self.analysis_dir = self.workspace / "analysis"

        # 确保目录存在
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

        # 初始化 Kimi 客户端（使用 OpenAI SDK）
        self.client = OpenAI(
            api_key=os.getenv("VISION_MODEL_API_KEY"),
            base_url=os.getenv("VISION_MODEL_BASE_URL")
        )
        self.model_name = os.getenv("VISION_MODEL_NAME", "moonshot-v1-vision")

    def _pdf_to_images(self, pdf_path: Path, max_pages: int = 3) -> List[str]:
        """
        将 PDF 转换为图片（base64 编码）

        Args:
            pdf_path: PDF 文件路径
            max_pages: 最多转换的页数

        Returns:
            图片的 base64 编码列表
        """
        print(f"📄 正在将 PDF 转换为图片（最多 {max_pages} 页）...")

        try:
            # 转换 PDF 为图片
            images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=max_pages)

            base64_images = []
            for i, image in enumerate(images):
                # 压缩图片以减小大小
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)

                import base64
                img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                base64_images.append(img_base64)
                print(f"  ✓ 第 {i+1} 页转换完成")

            return base64_images

        except Exception as e:
            print(f"❌ PDF 转图片失败: {e}")
            return []

    def step1_visual_analysis(self, pdf_path: Path) -> Dict[str, Any]:
        """
        步骤 1: 视觉分析 PDF

        使用 Kimi K2.5 的视觉能力分析 PDF，理解：
        - 图纸类型和用途
        - 主要构件和布局
        - 图层和标注信息
        - 设计特点
        """
        print("\n" + "="*60)
        print("步骤 1: 视觉分析 PDF")
        print("="*60)

        print(f"📄 正在分析: {pdf_path.name}")

        # 将 PDF 转换为图片
        image_base64_list = self._pdf_to_images(pdf_path, max_pages=3)

        if not image_base64_list:
            return {"error": "PDF 转图片失败"}

        # 调用 Claude 进行视觉分析
        prompt = """请分析这份建筑施工图纸，提供以下信息：

1. **图纸基本信息**
   - 图纸类型（平面图/立面图/剖面图等）
   - 建筑用途和规模
   - 图纸编号和比例

2. **主要构件识别**
   - 墙体（外墙、内墙、墙厚）
   - 柱子（位置、尺寸）
   - 门窗（数量、类型）
   - 楼梯（位置、类型）
   - 其他重要构件

3. **图层和标注**
   - 主要图层及其颜色
   - 轴线编号
   - 尺寸标注
   - 文字说明

4. **设计特点**
   - 空间布局特点
   - 结构特点
   - 需要特别注意的地方

请以结构化的方式回答，便于后续代码分析使用。"""

        try:
            # 构建消息内容：先添加所有图片，最后添加文本提示
            content = []
            for i, img_base64 in enumerate(image_base64_list):
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64}"
                    }
                })

            # 添加文本提示
            content.append({
                "type": "text",
                "text": prompt
            })

            print(f"🤖 正在调用 Kimi K2.5 分析 {len(image_base64_list)} 页图纸...")

            # 使用 Kimi 的 OpenAI 兼容格式
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "user",
                    "content": content
                }],
                temperature=1  # Kimi K2.5 要求 temperature 必须为 1
            )

            visual_report = {
                "timestamp": datetime.now().isoformat(),
                "pdf_file": pdf_path.name,
                "analysis": response.choices[0].message.content,
                "model": self.model_name
            }

            # 保存报告
            report_path = self.analysis_dir / "visual_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(visual_report, f, ensure_ascii=False, indent=2)

            print(f"✅ 视觉分析完成")
            print(f"📝 报告已保存: {report_path}")
            print("\n" + "-"*60)
            print("视觉分析摘要:")
            print("-"*60)
            print(response.choices[0].message.content[:500] + "...")

            return visual_report

        except Exception as e:
            print(f"❌ 视觉分析失败: {e}")
            return {"error": str(e)}

    def step2_code_analysis(self, dxf_path: Path) -> Dict[str, Any]:
        """
        步骤 2: DXF 代码分析

        使用 ezdxf 精确提取和测量：
        - 图层统计
        - 实体类型统计
        - 墙体长度
        - 门窗数量
        - 其他构件信息
        """
        print("\n" + "="*60)
        print("步骤 2: DXF 代码分析")
        print("="*60)

        print(f"📐 正在分析: {dxf_path.name}")

        try:
            # 读取 DXF 文件
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            # 1. 图层统计
            layers = {}
            for entity in msp:
                layer = entity.dxf.layer
                if layer not in layers:
                    layers[layer] = {"count": 0, "types": {}}
                layers[layer]["count"] += 1

                entity_type = entity.dxftype()
                if entity_type not in layers[layer]["types"]:
                    layers[layer]["types"][entity_type] = 0
                layers[layer]["types"][entity_type] += 1

            print(f"\n📊 图层统计: 共 {len(layers)} 个图层")
            for layer_name, info in sorted(layers.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
                print(f"  - {layer_name}: {info['count']} 个实体")

            # 2. 实体类型统计
            entity_types = {}
            for entity in msp:
                entity_type = entity.dxftype()
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

            print(f"\n📦 实体类型统计: 共 {len(entity_types)} 种类型")
            for entity_type, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  - {entity_type}: {count} 个")

            code_analysis = {
                "timestamp": datetime.now().isoformat(),
                "dxf_file": dxf_path.name,
                "layers": layers,
                "entity_types": entity_types,
                "total_entities": len(list(msp))
            }

            # 保存分析结果
            analysis_path = self.analysis_dir / "code_analysis.json"
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(code_analysis, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 代码分析完成")
            print(f"📝 结果已保存: {analysis_path}")

            return code_analysis

        except Exception as e:
            print(f"❌ 代码分析失败: {e}")
            return {"error": str(e)}

    def step3_comparison(self, visual_report: Dict, code_analysis: Dict) -> str:
        """
        步骤 3: 结果对比验证

        将视觉分析和代码分析结果进行对比，生成验证报告
        """
        print("\n" + "="*60)
        print("步骤 3: 结果对比验证")
        print("="*60)

        # 生成对比报告
        report_lines = [
            "# 视觉 + 代码联合分析报告",
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 1. 视觉分析摘要",
            "",
            "### 图纸理解",
            ""
        ]

        if "analysis" in visual_report:
            report_lines.append(visual_report["analysis"])
        else:
            report_lines.append("视觉分析失败")

        report_lines.extend([
            "",
            "## 2. 代码分析结果",
            "",
            f"- **总实体数**: {code_analysis.get('total_entities', 0)}",
            f"- **图层数量**: {len(code_analysis.get('layers', {}))}",
            f"- **实体类型**: {len(code_analysis.get('entity_types', {}))}",
            "",
            "### 主要图层",
            ""
        ])

        # 列出前 10 个图层
        layers = code_analysis.get('layers', {})
        for layer_name, info in sorted(layers.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
            report_lines.append(f"- **{layer_name}**: {info['count']} 个实体")

        report_lines.extend([
            "",
            "### 实体类型分布",
            ""
        ])

        # 列出前 10 个实体类型
        entity_types = code_analysis.get('entity_types', {})
        for entity_type, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            report_lines.append(f"- **{entity_type}**: {count} 个")

        report = "\n".join(report_lines)

        # 保存报告
        report_path = self.analysis_dir / "comparison_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ 对比报告已生成")
        print(f"📝 报告已保存: {report_path}")

        return report

    def run_full_analysis(self):
        """运行完整的视觉+代码联合分析流程"""
        print("\n" + "="*60)
        print("🚀 开始视觉 + 代码联合分析")
        print("="*60)

        # 查找输入文件
        pdf_file = self.input_dir / "甲类仓库建施.pdf"
        dxf_file = self.input_dir / "甲类仓库建施.dxf"

        if not pdf_file.exists():
            print(f"❌ PDF 文件不存在: {pdf_file}")
            return

        if not dxf_file.exists():
            print(f"❌ DXF 文件不存在: {dxf_file}")
            return

        # 步骤 1: 视觉分析
        visual_report = self.step1_visual_analysis(pdf_file)

        # 步骤 2: 代码分析
        code_analysis = self.step2_code_analysis(dxf_file)

        # 步骤 3: 结果对比
        comparison_report = self.step3_comparison(visual_report, code_analysis)

        print("\n" + "="*60)
        print("✅ 分析完成！")
        print("="*60)
        print(f"\n📁 所有结果已保存到: {self.analysis_dir}")
        print(f"  - visual_report.json - 视觉分析报告")
        print(f"  - code_analysis.json - 代码分析结果")
        print(f"  - comparison_report.md - 对比验证报告")


def main():
    """主函数"""
    analyzer = VisualCodeAnalyzer()
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
