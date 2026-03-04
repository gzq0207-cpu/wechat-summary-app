# Railway 完整部署指南 - 手动配置版本

## 概述

本指南将一步步教你如何在 Railway 上部署 WeChat Summary 应用。

## ✅ 完成的准备工作

- ✅ 代码已推送到 GitHub: `gzq0207-cpu/wechat-summary-app`
- ✅ Dockerfile 已准备好
- ✅ railway.toml 配置文件已创建
- ✅ 数据库初始化代码已优化

## 🚀 Railway 部署步骤

### 第 1 步：在浏览器中打开 Railway Dashboard

打开: https://railway.app/dashboard

(如果未登录，使用 GitHub 授权登录)

### 第 2 步：创建新项目

1. 点击 **"New Project"** 按钮
2. 选择 **"Deploy from GitHub repo"**
3. 搜索并选择 **"gzq0207-cpu/wechat-summary-app"** 仓库
4. 点击 **"Deploy Now"**

> Railway 会自动检测代码中的 Dockerfile 和 railway.toml 配置文件

等待几秒钟，你应该看到项目被创建。

### 第 3 步：添加 PostgreSQL 数据库服务

这是关键步骤！没有数据库，应用无法启动。

1. 在 Railway Dashboard 中，你应该看到已创建的项目
2. 点击 **"+ New Service"** 按钮（右上角或项目内部）
3. 选择 **"Database"**
4. 选择 **"PostgreSQL"**
5. 等待 PostgreSQL 服务创建完成（约 2-3 分钟）

> **重要**: Railway 会自动为你的应用生成 `DATABASE_URL` 环境变量，后端会自动使用它

### 第 4 步：配置后端服务环境变量

1. 在 Railway Dashboard 中，找到后端服务 (名字为 `wechat-summary-app` 或类似)
2. 点击该服务

3. 在顶部选项卡中，选择 **"Variables"**

4. 查看是否已有 `DATABASE_URL` 变量（由 PostgreSQL 自动生成）
   - 如果有，很好！说明数据库连接正确
   - 如果没有，手动检查 PostgreSQL 服务是否成功创建

5. 添加以下环境变量（点击 "+ New Variable"）：

   ```
   FASTAPI_ENV=production
   SECRET_KEY=your-random-32-char-string-change-me
   LLM_PROVIDER=baidu
   BAIDU_API_KEY=your-baidu-api-key
   BAIDU_SECRET_KEY=your-baidu-secret-key
   SCHEDULE_TIMEZONE=Asia/Shanghai
   CRAWL_SCHEDULE_HOUR=9
   CRAWL_SCHEDULE_MINUTE=0
   ```

### 第 5 步：获取 LLM API 密钥

如果你还没有百度 API 密钥，按照以下步骤获取：

1. 访问: https://console.bce.baidu.com/qian/ais/console/index
2. 使用百度账户登录 (或注册新账户)
3. 点击 "创建应用"
4. 选择 "文心千帆应用服务"
5. 填写应用信息并创建
6. 在应用管理中，找到你的应用
7. 复制 **API Key** 和 **Secret Key**
8. 粘贴到 Railway 的 Variables 中

### 第 6 步：部署应用

1. 运行部署触发器。有两种方式：

   **方式 A**: 推送代码到 GitHub（自动触发）
   ```bash
   cd /workspace/wechat-summary-app
   git push origin main
   ```

   **方式 B**: 在 Railway Dashboard 中手动启动部署
   - 点击 **"Deployments"** 选项卡
   - 点击 **"Re-deploy Latest"** 或 **"+New Deployment"**

2. 等待部署完成（通常 5-15 分钟）
   - 查看部署状态: Railway Dashboard → **"Deployments"** 选项卡
   - 查看实时日志: 点击部署旁的 **"Logs"**

### 第 7 步：验证部署成功

部署完成后，你应该看到：

1. **生成的公网 URL**（形如: `https://xxx.railway.app`）

2. **验证应用是否正常运行：**

   访问: `https://您的URL/api/v1/docs`
   
   你应该看到 Swagger UI API 文档页面

3. **检查数据库连接：**

   看日志中是否包含: `"数据库表已创建"`
   
   如果看到这条信息，说明数据库连接成功！

4. **访问前端应用：**

   访问: `https://您的URL/`
   
   你应该看到应用的首页

### 第 8 步：验证功能

1. 打开应用首页
2. 创建一个公众号账户 (为了测试)
3. 添加一个微信公众号 URL
4. 在任务页面点击 "立即运行" 测试爬虫

---

## 🔧 如果出现问题

### 问题 1: "连接被拒绝" (Connection Refused)

**症状**: 应用日志显示 `psycopg2.OperationalError: connection refused`

**解决方案**:
1. 确认 PostgreSQL 服务已成功创建
2. 检查后端服务的 Variables 中 `DATABASE_URL` 是否存在
3. 尝试重新启动后端服务: Railway Dashboard → 后端服务 → Settings → "Restart Instance"

### 问题 2: TOML 解析错误

**症状**: 部署失败，错误信息包含 "parsing error"

**解决方案**:
1. 确保 `railway.toml` 使用的是 TOML 格式（不是 YAML）
2. 最新的 `railway.toml` 已经修复，确保代码是最新的

### 问题 3: LLM API 调用失败

**症状**: 摘要生成失败，错误信息包含 API 错误

**解决方案**:
1. 检查 BAIDU_API_KEY 和 BAIDU_SECRET_KEY 是否正确
2. 确保百度账户有足够的 API 调用额度
3. 检查应用日志获取详细错误信息

### 问题 4: 应用无法启动

**症状**: 部署成功但应用无法访问

**解决方案**:
1. 查看 Logs 选项卡，查看具体错误信息
2. 常见原因: 缺少必需的环境变量
3. 添加遗漏的变量并重新部署

---

## 📝 有用的 Railway 命令

如果你安装了 Railway CLI，可以使用这些命令：

```bash
# 查看项目状态
railway status

# 查看实时日志
railway logs --follow

# 打开 Railway Dashboard
railway open

# 列出环境变量
railway variables

# 部署特定分支
railway deploy --branch main
```

---

## ✨ 部署完成后

- 配置自定义域名 (可选): Railway Dashboard → Settings → Custom Domain
- 设置备份策略 (可选): 定期导出数据库
- 监控应用性能: Railway Dashboard 提供的监控工具

---

## 📞 进一步帮助

- Railway 官方文档: https://docs.railway.app
- 常见问题: 查看 `RAILWAY_DATABASE_FIX.md`
- 本地调试: 查看 `QUICKSTART.md`
