#!/usr/bin/env python3
"""
实验 05: 三层架构完整演示
========================

演示视觉感知 + 策略规划 + 代码操作的完整工作流程。

工作流程：
1. 感知层：Kimi K2.5 视觉分析（只调用一次）
2. 规划层：DeepSeek 策略生成（多次调用）
3. 操作层：ezdxf 数据提取（本地计算）
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.dxf_service import DXFService
from services.strategy_service import StrategyService
from openai import OpenAI
from dotenv import load_dotenv
from pdf2image import convert_from_path
import io

# 加载环境变量
load_dotenv(project_root / ".env")


class ThreeLayerArchitecture:
    """三层架构演示"""

    def __init__(self, workspace_dir: str = "temp_workspace"):
        self.workspace = Path(workspace_dir)
        self.input_dir = self.workspace / "input"
        self.analysis_dir = self.workspace / "analysis"

        # 确保目录存在
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

        # 初始化服务
        self.dxf_service = DXFService()
        self.strategy_service = StrategyService()

        # 初始化视觉模型客户端
        self.vision_client = OpenAI(
            api_key=os.getenv("VISION_MODEL_API_KEY"),
            base_url=os.getenv("VISION_MODEL_BASE_URL")
        )
        self.vision_model = os.getenv("VISION_MODEL_NAME", "kimi-k2.5")

        # 成本和性能监控
        self.metrics = {
            "start_time": None,
            "vision_cost": 0,
            "strategy_cost": 0,
            "total_tokens": 0
        }

    def layer1_perception(self, pdf_path: Path) -> dict:
        """
        感知层：使用 Kimi K2.5 进行视觉分析（只调用一次）

        成本优化：使用低分辨率图片（50 DPI）
        """
        print("\n" + "="*60)
        print("感知层：视觉分析（Kimi K2.5）")
        print("="*60)

        start_time = time.time()

        # 转换 PDF 为低分辨率图片（节省成本）
        print("📄 转换 PDF 为图片（50 DPI，低成本模式）...")
        images = convert_from_path(pdf_path, dpi=50, first_page=1, last_page=1)

        # 转换为 base64
        import base64
        buffer = io.BytesIO()
        images[0].save(buffer, format='JPEG', quality=70)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        print(f"✓ 图片大小: {len(img_base64) / 1024:.1f} KB")

        # 调用 Kimi K2.5
        print("🤖 调用 Kimi K2.5 进行视觉分析...")

        prompt = """请快速分析这份建筑图纸，提供：
1. 建筑类型和用途
2. 主要构件（墙体、楼梯、柱子等）
3. 关键图层名称
4. 建议的工程量计算策略

请简洁回答，重点突出关键信息。"""

        response = self.vision_client.chat.completions.create(
            model=self.vision_model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}},
                    {"type": "text", "text": prompt}
                ]
            }],
            temperature=1
        )

        analysis = response.choices[0].message.content
        elapsed = time.time() - start_time

        # 记录成本
        self.metrics["vision_cost"] = response.usage.total_tokens
        self.metrics["total_tokens"] += response.usage.total_tokens

        print(f"✅ 视觉分析完成（{elapsed:.1f}秒）")
        print(f"💰 Token 使用: {response.usage.total_tokens}")

        result = {
            "analysis": analysis,
            "tokens": response.usage.total_tokens,
            "time": elapsed
        }

        # 保存结果
        with open(self.analysis_dir / "01_perception.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    def layer2_planning(self, perception_result: dict, dxf_path: Path) -> dict:
        """
        规划层：使用 DeepSeek 生成提取策略（可多次调用）
        """
        print("\n" + "="*60)
        print("规划层：策略生成（DeepSeek）")
        print("="*60)

        start_time = time.time()

        # 先获取 DXF 基本信息
        print("📐 读取 DXF 文件信息...")
        dxf_info = self.dxf_service.extract_layer_info(str(dxf_path))

        # 生成策略
        print("🤖 调用 DeepSeek 生成提取策略...")
        strategy_result = self.strategy_service.generate_extraction_strategy(
            visual_report=perception_result,
            dxf_info=dxf_info
        )

        elapsed = time.time() - start_time

        # 记录成本
        if strategy_result["success"]:
            tokens = strategy_result["usage"]["total_tokens"]
            self.metrics["strategy_cost"] += tokens
            self.metrics["total_tokens"] += tokens
            print(f"✅ 策略生成完成（{elapsed:.1f}秒）")
            print(f"💰 Token 使用: {tokens}")
        else:
            print(f"❌ 策略生成失败: {strategy_result['error']}")

        # 保存结果
        with open(self.analysis_dir / "02_planning.json", 'w', encoding='utf-8') as f:
            json.dump(strategy_result, f, ensure_ascii=False, indent=2)

        return strategy_result

    def layer3_operation(self, dxf_path: Path) -> dict:
        """
        操作层：使用 ezdxf 精确提取数据（本地计算，无成本）
        """
        print("\n" + "="*60)
        print("操作层：数据提取（ezdxf）")
        print("="*60)

        start_time = time.time()

        # 提取墙体数据
        print("📐 提取墙体数据...")
        walls_result = self.dxf_service.extract_walls(str(dxf_path), layer="WALL")

        # 计算工程量
        if walls_result["success"]:
            quantities = self.dxf_service.calculate_quantities(walls_result["walls"])
            print(f"✅ 提取完成: {quantities['quantities']['count']} 个墙体实体")
            print(f"📏 总长度: {quantities['quantities']['total_length']} m")
        else:
            print(f"❌ 提取失败: {walls_result['error']}")
            quantities = {"success": False}

        elapsed = time.time() - start_time
        print(f"⏱️  耗时: {elapsed:.1f}秒（本地计算，无 API 成本）")

        result = {
            "walls": walls_result,
            "quantities": quantities,
            "time": elapsed
        }

        # 保存结果
        with open(self.analysis_dir / "03_operation.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    def generate_final_report(self, perception, planning, operation):
        """生成最终报告"""
        report_lines = [
            "# 三层架构分析报告",
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 1. 感知层结果",
            "",
            perception.get("analysis", "无"),
            "",
            "## 2. 规划层结果",
            "",
            planning.get("strategy", "无"),
            "",
            "## 3. 操作层结果",
            "",
            f"- 墙体数量: {operation['quantities']['quantities']['count']}",
            f"- 总长度: {operation['quantities']['quantities']['total_length']} m",
        ]

        report = "\n".join(report_lines)
        with open(self.analysis_dir / "04_final_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

    def run_full_pipeline(self):
        """运行完整的三层架构流程"""
        print("\n" + "="*60)
        print("🚀 三层架构完整演示")
        print("="*60)

        self.metrics["start_time"] = time.time()

        # 查找输入文件
        pdf_file = self.input_dir / "甲类仓库建施.pdf"
        dxf_file = self.input_dir / "甲类仓库建施.dxf"

        if not pdf_file.exists():
            print(f"❌ PDF 文件不存在: {pdf_file}")
            return

        if not dxf_file.exists():
            print(f"❌ DXF 文件不存在: {dxf_file}")
            return

        # 第一层：感知
        perception = self.layer1_perception(pdf_file)

        # 第二层：规划
        planning = self.layer2_planning(perception, dxf_file)

        # 第三层：操作
        operation = self.layer3_operation(dxf_file)

        # 生成最终报告
        self.generate_final_report(perception, planning, operation)

        total_time = time.time() - self.metrics["start_time"]
        print("\n" + "="*60)
        print("✅ 分析完成！")
        print("="*60)
        print(f"⏱️  总耗时: {total_time:.1f}秒")
        print(f"💰 总 Token: {self.metrics['total_tokens']}")
        print(f"   - 视觉层: {self.metrics['vision_cost']}")
        print(f"   - 规划层: {self.metrics['strategy_cost']}")
        print(f"\n📁 结果已保存到: {self.analysis_dir}")


def main():
    """主函数"""
    arch = ThreeLayerArchitecture()
    arch.run_full_pipeline()


if __name__ == "__main__":
    main()
