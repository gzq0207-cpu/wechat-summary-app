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

# 安装 Nginx 和必要工具
RUN apt-get update && apt-get install -y \
    nginx \
    postgresql-client \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建 nginx 日志目录和其他必要目录
RUN mkdir -p /var/log/nginx /var/run/nginx /var/cache/nginx /var/www/html \
    && chown -R www-data:www-data /var/log/nginx /var/run /var/cache/nginx /var/www/html \
    && chmod -R 755 /var/www/html

# 复制 Python 运行时环境
COPY --from=backend-builder /usr/lib /usr/lib
COPY --from=backend-builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# 复制前端构建结果到 Nginx
RUN mkdir -p /var/www/html
COPY --from=frontend-builder /app/frontend/dist/ /var/www/html/

# 验证前端文件是否存在
RUN ls -la /var/www/html/ || echo "WARNING: Frontend dist is empty"

# 复制后端应用代码
COPY backend/app ./app
COPY backend/.env.example .env

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# Expose only port 80 (Nginx)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD curl -f http://127.0.0.1:80/api/v1/ >/dev/null 2>&1 || exit 1

# 直接启动：Nginx + FastAPI
# 1. 验证 Nginx 配置
# 2. 启动 Nginx 在后台
# 3. 启动 FastAPI 在前台（作为 PID 1）
CMD ["/bin/sh", "-c", "\
  echo '======================================'; \
  echo 'WeChat Summary App - Starting'; \
  echo '======================================'; \
  echo '[1/3] Testing Nginx configuration...'; \
  nginx -t || exit 1; \
  echo '[2/3] Starting Nginx on port 80...'; \
  nginx -g 'daemon off;' > /tmp/nginx.log 2>&1 & \
  NGINX_PID=$!; \
  sleep 2; \
  if ! ps -p $NGINX_PID > /dev/null 2>&1; then \
    echo '[ERROR] Nginx failed to start!'; \
    cat /var/log/nginx/error.log 2>&1 || cat /tmp/nginx.log 2>&1; \
    exit 1; \
  fi; \
  echo \"[OK] Nginx running (PID: $NGINX_PID)\"; \
  echo '[3/3] Starting FastAPI on 127.0.0.1:8000...'; \
  echo '======================================'; \
  exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info \
"]
