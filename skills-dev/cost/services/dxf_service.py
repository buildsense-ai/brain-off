#!/usr/bin/env python3
"""
DXF 数据提取服务

提供 DXF 文件的读取、解析和数据提取功能。
这是操作层的核心服务，负责精确提取 CAD 图纸中的几何数据。
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts import Modelspace


class DXFService:
    """DXF 数据提取服务"""

    def __init__(self):
        """初始化 DXF 服务"""
        pass

    def read_dxf(self, dxf_path: str) -> Dict[str, Any]:
        """
        读取 DXF 文件并返回基本信息

        Args:
            dxf_path: DXF 文件路径

        Returns:
            包含文件信息的字典
        """
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            return {
                "success": True,
                "file_path": dxf_path,
                "dxf_version": doc.dxfversion,
                "total_entities": len(list(msp)),
                "doc": doc,
                "msp": msp
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def extract_layer_info(self, dxf_path: str) -> Dict[str, Any]:
        """
        提取 DXF 文件的图层信息

        Args:
            dxf_path: DXF 文件路径

        Returns:
            图层统计信息
        """
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            # 统计图层信息
            layers = {}
            for entity in msp:
                layer = entity.dxf.layer
                if layer not in layers:
                    layers[layer] = {
                        "count": 0,
                        "types": {}
                    }
                layers[layer]["count"] += 1

                entity_type = entity.dxftype()
                if entity_type not in layers[layer]["types"]:
                    layers[layer]["types"][entity_type] = 0
                layers[layer]["types"][entity_type] += 1

            return {
                "success": True,
                "layers": layers,
                "total_layers": len(layers)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def extract_walls(self, dxf_path: str, layer: str = "WALL") -> Dict[str, Any]:
        """
        提取墙体数据

        Args:
            dxf_path: DXF 文件路径
            layer: 墙体所在图层名称

        Returns:
            墙体数据列表
        """
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            walls = []
            for entity in msp:
                if entity.dxf.layer == layer:
                    wall_data = {
                        "type": entity.dxftype(),
                        "layer": entity.dxf.layer
                    }

                    # 提取几何信息
                    if entity.dxftype() == "LINE":
                        wall_data["start"] = (entity.dxf.start.x, entity.dxf.start.y)
                        wall_data["end"] = (entity.dxf.end.x, entity.dxf.end.y)
                        wall_data["length"] = entity.dxf.start.distance(entity.dxf.end)
                    elif entity.dxftype() == "POLYLINE":
                        points = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices]
                        wall_data["points"] = points
                        # 计算总长度
                        total_length = 0
                        for i in range(len(points) - 1):
                            dx = points[i+1][0] - points[i][0]
                            dy = points[i+1][1] - points[i][1]
                            total_length += (dx**2 + dy**2)**0.5
                        wall_data["length"] = total_length

                    walls.append(wall_data)

            return {
                "success": True,
                "walls": walls,
                "total_count": len(walls)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def calculate_quantities(self, entities: List[Dict]) -> Dict[str, Any]:
        """
        计算工程量

        Args:
            entities: 实体数据列表

        Returns:
            工程量统计
        """
        try:
            total_length = 0
            total_area = 0
            count = len(entities)

            for entity in entities:
                if "length" in entity:
                    total_length += entity["length"]
                if "area" in entity:
                    total_area += entity["area"]

            return {
                "success": True,
                "quantities": {
                    "count": count,
                    "total_length": round(total_length, 2),
                    "total_area": round(total_area, 2)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 工具函数定义（供 LLM 调用）
TOOL_DEFINITIONS = [
    {
        "name": "extract_dxf_layer_info",
        "description": "提取 DXF 文件的图层信息，包括图层名称、实体数量和类型统计",
        "parameters": {
            "type": "object",
            "properties": {
                "dxf_path": {
                    "type": "string",
                    "description": "DXF 文件的路径"
                }
            },
            "required": ["dxf_path"]
        }
    },
    {
        "name": "extract_dxf_walls",
        "description": "从 DXF 文件中提取墙体数据，包括位置、长度等信息",
        "parameters": {
            "type": "object",
            "properties": {
                "dxf_path": {
                    "type": "string",
                    "description": "DXF 文件的路径"
                },
                "layer": {
                    "type": "string",
                    "description": "墙体所在的图层名称，默认为 WALL"
                }
            },
            "required": ["dxf_path"]
        }
    }
]
