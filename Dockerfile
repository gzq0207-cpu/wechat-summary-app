# 多阶段构建：前端 + 后端 + Nginx

# 阶段 1: 构建前端
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# 复制前端依赖
COPY frontend/package.json ./

# 安装依赖
RUN npm install

# 复制前端源代码
COPY frontend/src ./src
COPY frontend/*.config.js ./
COPY frontend/vite.config.ts ./
COPY frontend/tsconfig*.json ./
COPY frontend/index.html ./

# 构建前端
RUN npm run build

# 阶段 2: 构建后端
FROM python:3.11-slim as backend-builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium

# 阶段 3: 最终运行阶段（包含后端 + 前端 + Nginx）
FROM python:3.11-slim

WORKDIR /app

# 安装 Nginx
RUN apt-get update && apt-get install -y \
    nginx \
    postgresql-client \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 复制 Python 运行时环境
COPY --from=backend-builder /usr/lib /usr/lib
COPY --from=backend-builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# 复制前端构建结果到 Nginx
RUN mkdir -p /var/www/html
COPY --from=frontend-builder /app/frontend/dist /var/www/html

# 复制后端应用代码
COPY backend/app ./app
COPY backend/.env.example .env

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 创建启动脚本
RUN mkdir -p /app/scripts && cat > /app/scripts/start.sh << 'EOF'
#!/bin/bash
# 启动 Nginx（提供前端）
nginx -g "daemon off;" &
NGINX_PID=$!

# 启动 FastAPI 后端
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF
RUN chmod +x /app/scripts/start.sh

# 暴露端口
EXPOSE 80 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/status')" || exit 1

# 启动脚本
CMD ["/app/scripts/start.sh"]
