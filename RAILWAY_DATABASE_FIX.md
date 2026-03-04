# Railway PostgreSQL 部署修复指南

## 问题诊断
您正在看到此错误：
```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

**原因**：Railway 上没有链接 PostgreSQL 数据库服务，或者 `DATABASE_URL` 环境变量未设置。

---

## ✅ 快速修复步骤

### 第一步：添加 PostgreSQL 数据库（在 Railway Dashboard）

1. 打开 Railway Dashboard: https://railway.app/dashboard
2. 找到你的项目 `wechat-summary-app`
3. 点击 **"+ New Service"** 按钮（项目右上角）
4. 选择 **"Database"** 选项
5. 选择 **"PostgreSQL"**
6. 等待 PostgreSQL 服务创建完成（通常 1-2 分钟）

📌 **重要**：Railway 会自动注入 `DATABASE_URL` 环境变量给你的后端服务

### 第二步：验证 DATABASE_URL 已设置

1. 在 Railway Dashboard 中，点击你的**后端服务**
2. 切换到 **"Variables"** 选项卡
3. 你应该看到 `DATABASE_URL` 变量（格式类似：`postgresql://user:pass@hostname:port/dbname`）
4. 如果没看到，点击 **"Add Variable"** 并从 PostgreSQL 服务中手动复制

### 第三步：配置其他环境变量

在后端服务的 **"Variables"** 中，添加以下变量：

```plaintext
FASTAPI_ENV=production
SECRET_KEY=your-random-secret-key-here

# LLM 配置
LLM_PROVIDER=baidu
BAIDU_API_KEY=你的百度API密钥
BAIDU_SECRET_KEY=你的百度Secret密钥

# 爬虫配置
CRAWL_SCHEDULE_HOUR=9
CRAWL_SCHEDULE_MINUTE=0
SCHEDULE_TIMEZONE=Asia/Shanghai
```

💡 **如何获取百度 API 密钥**：
- 访问 https://console.bce.baidu.com/
- 登录账户 → 申请文心千帆 API
- 在应用管理中复制 API Key 和 Secret Key

### 第四步：拉取最新代码並触发重新部署

**选项 A：推送代码到 GitHub（自动部署）**
```bash
cd /workspace/wechat-summary-app
git pull origin main
git push origin main
```

**选项 B：在 Railway 中手动重新部署**
1. Railway Dashboard → 后端服务 → **"Deployments"** 选项卡
2. 找到最新部署（可能显示为失败）
3. 点击 **"Re-deploy"** 或 **"Retry"** 按钮
4. 等待新部署完成（5-10 分钟）

### 第五步：验证部署成功

1. 等待部署完成（查看 Deployments 选项卡中的状态）
2. 部署完成后，Railway 会显示你的应用 URL（如 `https://xxx.railway.app`）
3. 访问该 URL 验证应用是否启动
4. 打开 API 文档验证：`https://你的URL/api/v1/docs`
5. 查看实时日志确认数据库连接成功：Railway Dashboard → **"Logs"** 选项卡

---

## 🔍 如果仍然无法工作

### 检查清单

- [ ] PostgreSQL 服务显示在 Railway 项目的服务列表中
- [ ] `DATABASE_URL` 变量在后端服务中可见
- [ ] `BAIDU_API_KEY` 和 `BAIDU_SECRET_KEY` 已设置
- [ ] 最新的代码已推送到 GitHub（包括本修复）
- [ ] 部署日志中没有 TOML 解析错误

### 查看详细日志

1. Railway Dashboard → 后端服务 → **"Logs"** 选项卡
2. 搜索关键词：
   - `"数据库表已创建"`（成功迹象）
   - `"数据库初始化失败"`（检查下一步）
   - `"OperationalError"`（数据库连接问题）

### 手动重启应用

1. Railway Dashboard → 后端服务
2. 点击右上角 **"Settings"** → **"Restart Instance"**
3. 等待应用重新启动

---

## 📝 本次修复包含的更改

我已经提交了以下更新到你的 GitHub 仓库：

1. **🔧 database initialization 改进**
   - 数据库表创建失败时不会中断应用启动
   - 添加了更详细的错误日志
   - 文件：`backend/app/main.py`

2. **📖 Railway 部署文档优化**
   - 详细的 PostgreSQL 链接步骤
   - 环境变量配置表
   - 故障排查指南
   - 文件：`DEPLOYMENT.md`

---

## 🚀 如何验证完整的应用功能

部署成功后：

1. **访问前端**：`https://你的URL/`
2. **访问 API 文档**：`https://你的URL/api/v1/docs`（Swagger UI）
3. **添加公众号**：通过前端界面或 API 添加微信公众号
4. **手动触发爬虫**：在任务页面点击"立即运行"
5. **检查数据库**：
   - 访问 Railway PostgreSQL 服务
   - 查看 `public_accounts` 表是否有数据

---

## 💬 常见问题

**Q: 部署后访问 URL 显示 "502 Bad Gateway"**
A: 应用可能还在启动或数据库连接失败。检查 Logs 查看具体错误。

**Q: "CONNECTION REFUSED" 错误持续出现**
A: 
1. 确认 PostgreSQL 服务已完全创建（可能需要 2-3 分钟）
2. 在 Variables 中验证 `DATABASE_URL` 格式正确
3. 尝试在 Railway 中重启应用实例

**Q: API 调用返回 500 错误**
A: 检查 Logs 中的详细错误消息，通常是 LLM API 密钥配置问题

---

## 📞 需要进一步帮助？

检查完整的部署文档：[DEPLOYMENT.md](./DEPLOYMENT.md)

或查看项目完成总结：[COMPLETION.md](./COMPLETION.md)
