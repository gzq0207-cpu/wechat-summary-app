# 🚀 Railway 快速设置清单 (5分钟完成)

## ① 打开 Railway Dashboard (2分钟)

打开浏览器访问: **https://railway.app/dashboard**

使用 GitHub 账户授权登录

## ② 创建项目 (1分钟)

1. 点击 **"+ New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 搜索: **gzq0207-cpu/wechat-summary-app**
4. 点击 **"Deploy Now"**

> ✅ Railway 会自动检测到 Dockerfile 和 railway.toml

## ③ 添加 PostgreSQL 数据库 (2分钟)

等项目部署后（看到一个container）：

1. 点击 **"+ New Service"** 按钮
2. 选择 **"Database"** → **"PostgreSQL"**
3. 点击 **"Create"** 后等待 2-3 分钟

PostgreSQL 服务创建完成后，Railway 会**自动**给后端注入 `DATABASE_URL` 变量。

## ④ 配置环境变量 (1分钟)

1. 点击后端服务 (名称: wechat-summary-app 或类似)
2. 切换到 **"Variables"** 标签
3. 验证 **`DATABASE_URL`** 已存在（由 PostgreSQL 自动生成）
4. 点击 **"+ New Variable"** 添加这些变量:

```
FASTAPI_ENV=production
SECRET_KEY=<在下方获取>
LLM_PROVIDER=baidu
BAIDU_API_KEY=<从百度获取>
BAIDU_SECRET_KEY=<从百度获取>
SCHEDULE_TIMEZONE=Asia/Shanghai
CRAWL_SCHEDULE_HOUR=9
CRAWL_SCHEDULE_MINUTE=0
```

## ⚙️ 获取所需的密钥

### 生成 SECRET_KEY

在你的电脑运行一个命令生成 32 字符的随机字符串：

**Windows PowerShell:**
```powershell
[guid]::NewGuid().ToString().Replace('-','') + [guid]::NewGuid().ToString().Replace('-','')
```

**Mac/Linux:**
```bash
openssl rand -hex 32
```

复制结果粘贴到 `SECRET_KEY` 变量中。

### 获取百度 API 密钥

1. 打开: https://console.bce.baidu.com/
2. 点击 **"新增应用"**
3. 选择 **"文心千帆"** 产品下的任何 API
4. 填写应用名称后点击创建
5. 在应用列表中找到你的应用，复制:
   - **API Key** → 粘贴到 `BAIDU_API_KEY`
   - **Secret Key** → 粘贴到 `BAIDU_SECRET_KEY`

> 如果没有百度账户，需要先注册。百度免费提供部分额度供测试。

## ✅ 验证部署成功

### 等待部署完成

1. 点击 **"Deployments"** 标签
2. 看到绿色的 ✅ 表示部署成功
3. 部署通常需要 5-15 分钟

### 访问应用

部署完成后，你会看到一个公网 URL，类似:
```
https://wechat-summary-xxxxx.railway.app
```

**验证步骤:**

1. 打开 API 文档: `https://你的URL/api/v1/docs`
   - 应该看到 Swagger UI 界面 ✅

2. 打开前端应用: `https://你的URL/`
   - 应该看到应用首页 ✅

3. 查看日志确认数据库连接:
   - 点击 **"Logs"** 标签
   - 搜索: `"数据库表已创建"`
   - 看到这条信息说明数据库连接成功 ✅

## 🎯 功能测试

1. 点击 "FeedPage" (或导航栏的第二个菜单)
2. 点击 "+ 添加公众号"
3. 输入任意测试数据
4. 在 "TasksPage" 点击 "立即运行" 测试爬虫

## 📱 如果有问题

查看详细故障排查: **RAILWAY_DATABASE_FIX.md** 或 **RAILWAY_SETUP_MANUAL.md**

---

## 完成！🎉

你的应用现在在线了！每次推送代码到 GitHub，Railway 都会自动重新部署。
