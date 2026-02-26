#!/bin/bash
# Issue Manager API Server 启动脚本

cd "$(dirname "$0")"

# 检查依赖
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "安装依赖..."
    pip3 install -r requirements.txt
fi

echo "启动 Issue Manager API Server..."
echo "API 地址: http://localhost:8787"
echo "按 Ctrl+C 停止"

python3 -m uvicorn api:app --host 0.0.0.0 --port 8787 --reload
