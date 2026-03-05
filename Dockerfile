# 多阶段构建：前端 + 后端（Railway 自带反向代理，无需 Nginx）

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

# 阶段 2: 构建后端 + 安装 Playwright 浏览器
FROM python:3.11-slim as backend-builder

WORKDIR /app

# 安装系统依赖（含 Playwright 所需构建工具）
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器及其系统依赖（--with-deps 自动处理 OS 级依赖）
RUN playwright install --with-deps chromium

# 阶段 3: 最终运行阶段（FastAPI 同时提供 API 和前端静态文件）
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖（Chromium 所需的 .so 库 + 数据库客户端 + curl）
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq5 \
    curl \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    libxss1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# 复制 Python 运行时环境
COPY --from=backend-builder /usr/lib /usr/lib
COPY --from=backend-builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# 复制 Playwright Chromium 浏览器二进制（修复爬虫功能）
COPY --from=backend-builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# 复制前端构建结果到 /app/static（由 FastAPI StaticFiles 提供服务）
COPY --from=frontend-builder /app/frontend/dist/ /app/static/

# 验证前端文件是否存在
RUN ls -la /app/static/ || echo "WARNING: Frontend dist is empty"

# 复制后端应用代码
COPY backend/app ./app
COPY backend/.env.example .env

# 暴露端口（Railway 通过 $PORT 环境变量动态路由，8000 是本地运行的默认值）
EXPOSE 8000

# 健康检查（Railway 使用 railway.toml 的 healthcheckPath，此处供本地 docker run 使用）
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

# Railway 会用 railway.toml 的 startCommand 覆盖此 CMD
# 此 CMD 仅用于本地 docker run 的回退
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
