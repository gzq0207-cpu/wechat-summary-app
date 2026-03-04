# Windows部署脚本
@echo off
setlocal enabledelayedexpansion

echo =========================================
echo WeChat Summary 应用部署脚本
echo =========================================

REM 检查Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Docker 未安装或未在PATH中
    exit /b 1
)

REM 检查环境变量文件
if not exist "backend\.env" (
    echo ⚠️  警告: backend\.env 不存在，复制from .env.example
    copy backend\.env.example backend\.env
)

echo 📦 构建Docker镜像...
docker-compose build
if errorlevel 1 goto error

echo 🚀 启动服务...
docker-compose up -d
if errorlevel 1 goto error

echo ⏳ 等待服务启动...
timeout /t 10 /nobreak

echo ✅ 创建数据库表...
docker-compose exec -T backend python -c "from app.core.config import engine, Base; Base.metadata.create_all(bind=engine); print('数据库表已创建')"

echo.
echo =========================================
echo ✅ 部署完成！
echo =========================================
echo 后端: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 前端: http://localhost:5173
echo =========================================
echo.
echo 常用命令:
echo   docker-compose logs -f           # 查看日志
echo   docker-compose ps                # 查看运行容器
echo   docker-compose stop              # 停止服务
echo   docker-compose down              # 删除容器
echo.

goto end

:error
echo ❌ 部署失败
exit /b 1

:end
endlocal
