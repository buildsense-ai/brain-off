#!/usr/bin/env python3
"""
策略生成服务

使用 DeepSeek LLM 基于视觉分析结果生成 DXF 数据提取策略。
这是规划层的核心服务，负责将视觉理解转化为可执行的代码计划。
"""

import os
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class StrategyService:
    """策略生成服务"""

    def __init__(self):
        """初始化策略服务"""
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        self.model = "deepseek-chat"

    def generate_extraction_strategy(
        self,
        visual_report: Dict[str, Any],
        dxf_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        基于视觉分析结果生成提取策略

        Args:
            visual_report: 视觉分析报告
            dxf_info: DXF 文件基本信息

        Returns:
            提取策略
        """
        try:
            # 构建提示词
            prompt = self._build_strategy_prompt(visual_report, dxf_info)

            # 调用 DeepSeek
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个建筑工程量计算专家，擅长分析 CAD 图纸并制定数据提取策略。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )

            strategy_text = response.choices[0].message.content

            return {
                "success": True,
                "strategy": strategy_text,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _build_strategy_prompt(
        self,
        visual_report: Dict[str, Any],
        dxf_info: Dict[str, Any]
    ) -> str:
        """
        构建策略生成的提示词

        Args:
            visual_report: 视觉分析报告
            dxf_info: DXF 文件信息

        Returns:
            提示词文本
        """
        prompt = f"""
请基于以下信息，制定 DXF 数据提取和工程量计算策略：

## 视觉分析结果
{visual_report.get('analysis', '无视觉分析结果')}

## DXF 文件信息
- 总实体数: {dxf_info.get('total_entities', 0)}
- 图层数量: {dxf_info.get('total_layers', 0)}
- 主要图层: {', '.join(list(dxf_info.get('layers', {}).keys())[:10])}

## 请提供以下内容：

1. **关键构件识别**
   - 列出需要提取的主要构件（如外墙、内墙、楼梯、柱子等）
   - 每个构件对应的图层名称

2. **提取优先级**
   - 按重要性排序，哪些构件应该优先提取

3. **计算策略**
   - 每个构件需要计算什么（长度、面积、体积等）
   - 特殊处理方法（如外墙和内墙的区分）

4. **验证方法**
   - 如何验证提取结果的合理性

请以结构化的方式回答，便于后续代码实现。
"""
        return prompt

    def create_execution_plan(
        self,
        strategy: str,
        dxf_layers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        基于策略创建可执行的提取计划

        Args:
            strategy: 策略文本
            dxf_layers: DXF 图层信息

        Returns:
            执行计划
        """
        try:
            prompt = f"""
基于以下策略和 DXF 图层信息，生成具体的执行计划：

## 策略
{strategy}

## 可用图层
{list(dxf_layers.keys())}

请生成 JSON 格式的执行计划，格式如下：
{{
  "tasks": [
    {{
      "component": "外墙",
      "layer": "WALL",
      "entity_type": "POLYLINE",
      "calculation": "length",
      "priority": 1
    }}
  ]
}}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个 JSON 生成专家，只返回有效的 JSON 格式。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )

            import json
            plan_text = response.choices[0].message.content
            # 提取 JSON（可能包含在 markdown 代码块中）
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0].strip()

            plan = json.loads(plan_text)

            return {
                "success": True,
                "plan": plan,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 工具函数定义
TOOL_DEFINITIONS = [
    {
        "name": "generate_extraction_strategy",
        "description": "基于视觉分析结果生成 DXF 数据提取策略",
        "parameters": {
            "type": "object",
            "properties": {
                "visual_report": {
                    "type": "object",
                    "description": "视觉分析报告"
                },
                "dxf_info": {
                    "type": "object",
                    "description": "DXF 文件基本信息"
                }
            },
            "required": ["visual_report", "dxf_info"]
        }
    }
]


