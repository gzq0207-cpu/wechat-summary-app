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

# 创建 Python 启动脚本（比 shell 更可靠）
RUN cat > /startup.py << 'PYEOF'
#!/usr/bin/env python3
"""
启动脚本：Nginx + FastAPI
确保 Nginx 在前台模式下监听 80 端口，FastAPI 监听 127.0.0.1:8000
"""
import subprocess
import sys
import time
import signal
import os

print("="*50)
print("WeChat Summary App - Starting")
print("="*50)

# Step 1: Validate Nginx
print("\n[1/3] Testing Nginx configuration...")
result = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
if result.returncode != 0:
    print("[ERROR] Nginx configuration test failed!")
    print(result.stderr)
    sys.exit(1)
print("[OK] Nginx configuration is valid")

# Step 2: Start Nginx in background (WITHOUT daemon off - that would block)
print("[2/3] Starting Nginx on port 80...")
# Use daemon on (default) so Nginx backgrounds itself immediately
nginx_proc = subprocess.Popen(
    ["nginx"],  # No "daemon off" - let nginx background itself
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    preexec_fn=lambda: None  # Ensure it runs independently
)
time.sleep(2)

if nginx_proc.poll() is not None:
    stdout, stderr = nginx_proc.communicate()
    print("[ERROR] Nginx failed to start!")
    print("STDOUT:", stdout.decode() if stdout else "")
    print("STDERR:", stderr.decode() if stderr else "")
    sys.exit(1)

print(f"[OK] Nginx running (PID: {nginx_proc.pid})")

# Step 3: Start FastAPI in foreground
print("[3/3] Starting FastAPI on 127.0.0.1:8000...")
print("="*50 + "\n")

# Use os.execvp to replace this process with FastAPI
# This ensures FastAPI becomes PID 1 and its signals are handled directly
os.execvp("uvicorn", [
    "uvicorn",
    "app.main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--log-level", "info"
])
PYEOF

RUN chmod +x /startup.py

# Expose only port 80 (Nginx)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD curl -f http://127.0.0.1:80/api/v1/ >/dev/null 2>&1 || exit 1

# Run the Python startup script
CMD ["python3", "/startup.py"]
