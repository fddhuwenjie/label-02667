#!/bin/bash

echo "=== SQL数据库管理器启动脚本 ==="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 检测Python命令
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "错误: 未找到Python，请先安装Python 3"
    read -p "按回车键退出..."
    exit 1
fi

echo "使用Python: $PYTHON"

# 检测pip命令
if command -v pip3 &> /dev/null; then
    PIP=pip3
elif command -v pip &> /dev/null; then
    PIP=pip
else
    echo "错误: 未找到pip，请先安装pip"
    read -p "按回车键退出..."
    exit 1
fi

# 启动MySQL容器
echo "启动MySQL数据库..."
docker-compose -f "$SCRIPT_DIR/docker-compose.yml" up -d

# 等待MySQL就绪
echo "等待MySQL启动..."
sleep 5

# 安装依赖
echo "安装Python依赖..."
$PIP install -r "$SCRIPT_DIR/frontend-admin/requirements.txt" -q 2>/dev/null

# 启动GUI
echo "启动GUI应用..."
echo "----------------------------------------"
$PYTHON "$SCRIPT_DIR/frontend-admin/app/main.py"
