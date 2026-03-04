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

3. **配置服务**
   - Railway会自动检测 `railway.toml` 配置
   - 自动创建 PostgreSQL 数据库服务
   - 自动构建并部署 Docker 镜像

4. **设置环境变量**
   在 Railway Dashboard 的 "Variables" 中配置:
   ```
   FASTAPI_ENV=production
   SECRET_KEY=your-random-secret-key-here
   LLM_PROVIDER=baidu
   BAIDU_API_KEY=your-baidu-api-key
   BAIDU_SECRET_KEY=your-baidu-secret-key
   SCHEDULE_TIMEZONE=Asia/Shanghai
   ```
   
   Railway 会自动生成: `DATABASE_URL`

5. **部署**
   - 推送代码到GitHub即自动部署
   - 查看日志: Railway Dashboard → Logs

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

### 常见问题

**1. 数据库连接失败**
- 检查 DATABASE_URL 格式
- 确保数据库服务已启动: `docker-compose ps`
- 查看数据库日志: `docker-compose logs postgres`

**2. LLM API 调用失败**
- 检查 API 密钥是否正确
- 确保账户有充足的额度
- 查看后端日志获取详细错误信息

**3. Playwright 浏览器超时**
- 增加 BROWSER_TIMEOUT_SECONDS
- 检查网络连接
- 减少爬取频率

**4. 前后端通信失败**
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
