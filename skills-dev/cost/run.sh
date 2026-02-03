#!/bin/bash
# 工程造价 Agent 启动脚本

echo "🏗️  启动工程造价 Agent..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查依赖
if ! python3 -c "import sqlalchemy" 2>/dev/null; then
    echo "⚠️  检测到缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
fi

# 检查环境变量
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，从模板创建..."
    cp .env.example .env
    echo "📝 请编辑 .env 文件，配置 API Key"
    echo ""
fi

# 运行 Agent
python3 cost_agent.py
