# 云部署部署指南

## Railway 部署（推荐 - 完全云端）

### 优势
- ✅ 自动化部署流程
- ✅ 内置PostgreSQL数据库服务
- ✅ SSL证书自动配置
- ✅ 环境变量管理方便
- ✅ 日志和监控集成

### 部署步骤

1. **连接GitHub**
   - 推送项目代码到GitHub
   - 在 https://railway.app 创建账户
   
2. **创建项目**
   - 点击 "New Project" 
   - 选择 "Deploy from GitHub repo"
   - 选择 `wechat-summary-app` 仓库

3. **添加PostgreSQL数据库服务**
   
   ⚠️ **重要**: Railway不会自动创建PostgreSQL，需要手动添加：
   
   - 在Railway Dashboard中选择项目
   - 点击 "+ New Service" → 选择 "Database" → 选择 "PostgreSQL"
   - 等待PostgreSQL服务创建完成（1-2分钟）
   - Railway会自动注入 `DATABASE_URL` 环境变量

4. **配置后端服务连接**
   
   连接后端服务到PostgreSQL：
   - 在Railway Dashboard中，找到你的后端服务
   - 点击 "Variable" 选项卡
   - 确认 `DATABASE_URL` 变量已自动设置（格式: `postgresql://user:password@hostname:5432/db_name`）
   - 如果没有，手动从PostgreSQL服务配置中复制 `DATABASE_URL`

5. **设置应用环境变量**
   
   在后端服务的 "Variable" 中配置以下额外变量:
   ```
   FASTAPI_ENV=production
   SECRET_KEY=your-random-secret-key-change-this
   LLM_PROVIDER=baidu
   BAIDU_API_KEY=your-baidu-api-key
   BAIDU_SECRET_KEY=your-baidu-secret-key
   SCHEDULE_TIMEZONE=Asia/Shanghai
   CRAWL_SCHEDULE_HOUR=9
   CRAWL_SCHEDULE_MINUTE=0
   ```
   
   | 变量名 | 获取方式 |
   |------|--------|
   | `BAIDU_API_KEY` | 从百度云控制台获取 |
   | `BAIDU_SECRET_KEY` | 从百度云控制台获取 |
   | `SECRET_KEY` | 生成随机字符串: `openssl rand -hex 32` |

6. **部署应用**
   
   - 将修改推送到GitHub: `git push origin main`
   - Railway会自动检测到更新并重新构建部署
   - 查看部署日志: Railway Dashboard → "Deployments" 标签
   - 等待部署完成（通常5-10分钟）

7. **验证部署**
   
   部署完成后：
   - Railway会生成一个公网URL（如: `https://xxx.railway.app`）
   - 打开该URL验证应用是否成功启动
   - 访问API文档: `https://xxx.railway.app/api/v1/docs`
   - 查看应用日志确认数据库连接成功: Railway Dashboard → "Logs"

## 阿里云 ECS 部署

### 前置要求
- 阿里云 ECS 实例（推荐 2核4GB）
- 安装 Docker 和 Docker Compose
- 开放安全组端口: 80, 443, 8000

### 部署步骤

1. **SSH到服务器**
   ```bash
   ssh ubuntu@your-ecs-ip
   ```

2. **安装Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

3. **克隆项目**
   ```bash
   git clone https://github.com/your-username/wechat-summary-app.git
   cd wechat-summary-app
   ```

4. **配置环境变量**
   ```bash
   # 创建 .env 文件
   cp backend/.env.example backend/.env
   
   # 编辑环境变量
   nano backend/.env
   ```
   
   关键变量:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/wechat_summary
   FASTAPI_ENV=production
   LLM_PROVIDER=baidu
   BAIDU_API_KEY=your-key
   BAIDU_SECRET_KEY=your-secret
   ```

5. **启动应用**
   ```bash
   # Linux/Mac
   chmod +x deploy.sh
   ./deploy.sh
   
   # Windows (使用WSL或PowerShell)
   ./deploy.bat
   ```

6. **配置反向代理（Nginx）**
   ```bash
   sudo apt-get install nginx
   
   # 复制nginx配置
   sudo cp nginx.conf /etc/nginx/sites-available/wechat-summary
   sudo ln -s /etc/nginx/sites-available/wechat-summary /etc/nginx/sites-enabled/
   
   sudo systemctl restart nginx
   ```

7. **配置SSL证书（Let's Encrypt）**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

8. **定时备份数据库**
   ```bash
   # 创建备份脚本
   cat > /home/ubuntu/backup-db.sh << 'EOF'
   #!/bin/bash
   BACKUP_DIR="/home/ubuntu/backups"
   mkdir -p $BACKUP_DIR
   docker-compose exec -T postgres pg_dump -U wechat_user wechat_summary | gzip > $BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).sql.gz
   EOF
   
   # 添加定时任务
   crontab -e
   # 添加: 0 2 * * * /home/ubuntu/backup-db.sh  (每天凌晨2点备份)
   ```

## 监控和维护

### 查看日志
```bash
# Docker容器日志
docker-compose logs -f backend

# Railway
# 在Railway Dashboard中查看实时日志
```

### 定时任务检查
后端会自动在每天 09:00 执行爬虫任务
可以在任务页面查看执行状态和日志

### 更新应用
```bash
# 拉取最新代码
git pull origin main

# 重新构建和启动
docker-compose down
docker-compose up -d --build
```

## 常见问题

**1. Railway部署失败: "connection refused on localhost:5432"**
   
   原因: PostgreSQL数据库服务未添加或未连接
   
   解决方案:
   ```
   1. 检查PostgreSQL是否已在Railway中创建:
      - 查看Railway项目的所有services
      - 应该看到 "PostgreSQL" 服务
      
   2. 如果没有PostgreSQL服务:
      - 点击 "+ New Service"
      - 选择 "Database" → "PostgreSQL"
      - 等待创建完成
      
   3. 确认DATABASE_URL已设置:
      - 点击后端服务 → "Variables"
      - 应该看到 DATABASE_URL 变量
      - 格式应为: postgresql://user:pass@hostname:port/dbname
      
   4. 重新部署后端:
      - Railway Dashboard → 后端服务 → "Deploy"
      - 或推送代码到GitHub触发自动部署
   ```

**2. Railway部署失败: "TOML parsing error"**
   
   原因: `railway.toml` 文件格式不正确
   
   解决方案:
   ```bash
   # 确保railway.toml使用正确的TOML格式（非YAML）:
   [build]
   dockerfile = "Dockerfile"
   context = "."

   [deploy]
   startCommand = "uvicorn app.main:app --host 0.0.0.0 --port 8000"

   [env]
   FASTAPI_ENV = "production"
   ```

**3. 数据库连接失败**
- 检查 DATABASE_URL 格式是否正确
- 确保 PostgreSQL 服务已启动并可达
- 查看Railway日志获取详细错误: Railway Dashboard → Logs
- 检查数据库用户名和密码是否正确

**4. LLM API 调用失败**
- 检查 BAIDU_API_KEY 和 BAIDU_SECRET_KEY 是否正确
- 确保账户有充足的API调用额度
- 查看后端日志获取详细错误信息

**5. Playwright 浏览器超时**
- 增加 BROWSER_TIMEOUT_SECONDS 变量值
- 检查网络连接
- 减少爬取频率或增加 CRAWL_DELAY_SECONDS

**6. 前后端通信失败**
- 检查CORS配置
- 确保前端API_URL指向正确的后端地址
- 查看浏览器开发工具中的网络请求

## 性能优化建议

1. **数据库优化**
   - 定期分析日志表（会增长很快）
   - 添加索引以加快查询
   - 定期清理旧数据

2. **爬虫优化**
   - 增加爬虫延迟以避免被封IP
   - 使用代理池轮换IP
   - 实现自动重试机制

3. **API缓存**
   - 使用Redis缓存热点数据
   - 设置合理的缓存过期时间

4. **前端优化**
   - 启用Gzip压缩
   - 使用CDN分发静态资源
   - 实现分页加载

## 安全建议

1. **认证和授权**
   - 为管理接口添加JWT认证
   - 限制API访问频率（Rate Limiting）

2. **数据保护**
   - 使用HTTPS加密传输
   - 定期备份数据库
   - 加密敏感信息（LLM密钥）

3. **爬虫安全**
   - 使用旋转代理避免被识别
   - 实现验证码识别和处理
   - 遵守网站robots.txt规则
