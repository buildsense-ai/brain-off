#!/usr/bin/env python3
"""
工程造价 Agent - 独立CLI入口

可以独立运行，也可以作为Skill集成到主系统
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# 导入工具函数
from tools import (
    load_cad_file,
    create_analysis_plan,
    convert_cad_to_image,
    analyze_drawing_visual,
    export_boq_to_excel,
    get_plan_context
)


class CostEstimationAgent:
    """工程造价Agent - 独立运行版本"""

    def __init__(self):
        self.current_plan_id = None
        self.current_project = None

    def welcome(self):
        """欢迎信息"""
        print("=" * 60)
        print("🏗️  工程造价 AI Agent")
        print("=" * 60)
        print("\n功能：")
        print("  1. 加载CAD图纸（DXF/DWG）")
        print("  2. 智能分析图纸内容")
        print("  3. 自动计算工程量")
        print("  4. 生成工程量清单")
        print("  5. 导出Excel报表")
        print("\n输入 'help' 查看命令，'quit' 退出")
        print("=" * 60)

    def show_help(self):
        """显示帮助信息"""
        print("\n可用命令：")
        print("  load <文件路径>     - 加载CAD文件")
        print("  analyze             - 分析当前图纸")
        print("  status              - 查看当前进度")
        print("  export              - 导出Excel清单")
        print("  new <项目名>        - 创建新项目")
        print("  resume <计划ID>     - 恢复之前的项目")
        print("  help                - 显示此帮助")
        print("  quit                - 退出程序")

    def load_file(self, file_path: str):
        """加载CAD文件"""
        print(f"\n📂 正在加载文件: {file_path}")

        result = load_cad_file(file_path)

        if result["success"]:
            print(f"✅ 文件加载成功！")
            print(f"   文件ID: {result['data']['file_id']}")
            return result["data"]["file_id"]
        else:
            print(f"❌ 加载失败: {result['error']}")
            return None

    def create_project(self, project_name: str, cad_file_id: str):
        """创建新项目"""
        print(f"\n📋 创建项目: {project_name}")

        result = create_analysis_plan(project_name, cad_file_id)

        if result["success"]:
            self.current_plan_id = result["data"]["plan_id"]
            self.current_project = project_name
            print(f"✅ 项目创建成功！")
            print(f"   计划ID: {self.current_plan_id}")
            print(f"\n待办任务：")
            for task in result["data"]["tasks"]["pending"]:
                print(f"   - {task}")
            return True
        else:
            print(f"❌ 创建失败: {result['error']}")
            return False

    def analyze_drawing(self):
        """分析图纸"""
        if not self.current_plan_id:
            print("❌ 请先创建项目或加载文件")
            return

        print(f"\n🔍 开始分析图纸...")
        print("   这可能需要几分钟时间...")

        # TODO: 实现完整的分析流程
        # 1. 转换为图片
        # 2. 视觉分析
        # 3. 提取实体
        # 4. 计算工程量
        # 5. 查询定额
        # 6. 生成清单

        print("⚠️  完整分析功能需要配置视觉模型API")
        print("   请参考 .env.example 配置 VISION_MODEL_API_KEY")

    def show_status(self):
        """显示当前状态"""
        if not self.current_plan_id:
            print("❌ 当前没有活动项目")
            return

        print(f"\n📊 项目状态")
        print(f"   项目名称: {self.current_project}")
        print(f"   计划ID: {self.current_plan_id}")

        result = get_plan_context(self.current_plan_id)

        if result["success"]:
            data = result["data"]
            tasks = data["tasks"]

            print(f"\n任务进度：")
            print(f"   ✅ 已完成: {len(tasks.get('completed', []))}")
            print(f"   🔄 进行中: {len(tasks.get('in_progress', []))}")
            print(f"   ⏳ 待办: {len(tasks.get('pending', []))}")

            if data.get("boq_items_count", 0) > 0:
                print(f"\n清单项目: {data['boq_items_count']} 项")
        else:
            print(f"❌ 获取状态失败: {result['error']}")

    def export_excel(self):
        """导出Excel"""
        if not self.current_plan_id:
            print("❌ 请先创建项目")
            return

        print(f"\n📤 导出Excel清单...")

        result = export_boq_to_excel(self.current_plan_id)

        if result["success"]:
            print(f"✅ 导出成功！")
            print(f"   文件路径: {result['data']['file_path']}")
            print(f"   清单项数: {result['data']['item_count']}")
            print(f"   总造价: ¥{result['data']['total_price']:,.2f}")
        else:
            print(f"❌ 导出失败: {result['error']}")

    def run(self):
        """主循环"""
        self.welcome()

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if command == "quit" or command == "exit":
                    print("\n👋 再见！")
                    break

                elif command == "help":
                    self.show_help()

                elif command == "load":
                    if not args:
                        print("❌ 请指定文件路径: load <文件路径>")
                    else:
                        file_id = self.load_file(args)
                        if file_id:
                            # 自动创建项目
                            project_name = Path(args).stem
                            self.create_project(project_name, file_id)

                elif command == "new":
                    if not args:
                        print("❌ 请指定项目名称: new <项目名>")
                    else:
                        print("⚠️  请先使用 load 命令加载CAD文件")

                elif command == "analyze":
                    self.analyze_drawing()

                elif command == "status":
                    self.show_status()

                elif command == "export":
                    self.export_excel()

                elif command == "resume":
                    if not args:
                        print("❌ 请指定计划ID: resume <计划ID>")
                    else:
                        self.current_plan_id = args
                        result = get_plan_context(args)
                        if result["success"]:
                            self.current_project = result["data"]["project_name"]
                            print(f"✅ 已恢复项目: {self.current_project}")
                            self.show_status()
                        else:
                            print(f"❌ 恢复失败: {result['error']}")

                else:
                    print(f"❌ 未知命令: {command}")
                    print("   输入 'help' 查看可用命令")

            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {str(e)}")


def main():
    """主入口"""
    agent = CostEstimationAgent()
    agent.run()


if __name__ == "__main__":
    main()
