#!/bin/bash
# 部署脚本 - 用于Railway或本地Docker部署

set -e  # 错误时停止执行

echo "========================================="
echo "WeChat Summary 应用部署脚本"
echo "========================================="

# 检查必要的命令
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 错误: $1 未安装"
        exit 1
    fi
}

# 检查Docker
check_command docker
check_command docker-compose

# 检查环境变量文件
if [ ! -f backend/.env ]; then
    echo "⚠️  警告: backend/.env 不存在，复制from .env.example"
    cp backend/.env.example backend/.env
fi

echo "📦 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "✅ 创建数据库表..."
docker-compose exec -T backend python -c "
from app.core.config import engine, Base
Base.metadata.create_all(bind=engine)
print('数据库表已创建')
"

echo ""
echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo "后端: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "前端: http://localhost:5173"
echo "========================================="
echo ""
echo "常用命令:"
echo "  docker-compose logs -f           # 查看日志"
echo "  docker-compose ps                # 查看运行容器"
echo "  docker-compose stop              # 停止服务"
echo "  docker-compose down              # 删除容器"
echo ""
