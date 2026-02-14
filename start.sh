#!/bin/bash

echo "=== SQL数据库管理器启动脚本 ==="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: 未找到Docker，请先安装Docker"
    exit 1
fi

# 检测Python命令
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "错误: 未找到Python，请先安装Python 3.9+"
    exit 1
fi

echo "Python: $PYTHON"

# 检测pip命令
if command -v pip3 &> /dev/null; then
    PIP=pip3
else
    PIP=pip
fi

# 启动MySQL容器
echo ""
echo "[1/4] 启动MySQL数据库容器..."
docker compose -f "$SCRIPT_DIR/docker-compose.yml" up -d mysql 2>/dev/null || \
docker-compose -f "$SCRIPT_DIR/docker-compose.yml" up -d mysql

# 等待MySQL完全就绪
echo ""
echo "[2/4] 等待MySQL启动完成..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # 使用 docker compose 的健康检查
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' 2667-mysql-1 2>/dev/null || \
             docker inspect --format='{{.State.Health.Status}}' 2667_mysql_1 2>/dev/null || \
             echo "starting")
    
    if [ "$HEALTH" = "healthy" ]; then
        echo "✓ MySQL已就绪"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  等待中... ($RETRY_COUNT/$MAX_RETRIES) 状态: $HEALTH"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "警告: MySQL健康检查超时，尝试继续启动..."
fi

# 安装依赖
echo ""
echo "[3/4] 安装Python依赖..."
$PIP install -r "$SCRIPT_DIR/frontend-admin/requirements.txt" -q 2>/dev/null

# 启动GUI
echo ""
echo "[4/4] 启动GUI应用..."
echo "========================================"
echo "连接信息:"
echo "  主机: localhost"
echo "  端口: 3306"
echo "  用户: root"
echo "  密码: root123"
echo "========================================"
echo ""

cd "$SCRIPT_DIR/frontend-admin"
$PYTHON -m app.main
