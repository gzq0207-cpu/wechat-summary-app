# 🚀 快速开始（5分钟部署）

## 云端部署（推荐 - 最快）

### Railway 部署（完全自动化）

**只需4步，5分钟内上线：**

1. **推送代码到GitHub**
   ```bash
   git push origin main
   ```

2. **连接Railway** 
   - 访问 https://railway.app
   - 点击 "New Project" → "Deploy from GitHub repo"
   - 选择本仓库

3. **Railway自动配置**
   - 自动检测 `railway.toml`
   - 自动创建PostgreSQL数据库
   - 自动分配DATABASE_URL

4. **设置LLM密钥**
   
   在Railway Dashboard的 Variables 标签页添加：
   ```
   LLM_PROVIDER=baidu
   BAIDU_API_KEY=你的密钥
   BAIDU_SECRET_KEY=你的密钥
   SECRET_KEY=random-string-here
   ```
   
   获取百度密钥：
   - 访问 https://cloud.baidu.com/
   - 申请文心千帆API
   - 复制API Key和Secret Key

**完成！** 应用会自动部署，查看URL即可访问 ✅

---

## 本地快速开始

### 前置要求
- Docker & Docker Compose
- （或手动安装 Python 3.11+ 和 Node.js 18+）

### 一键启动

```bash
# 1. 复制环境变量
cp backend/.env.example backend/.env

# 2. 编辑环境变量（填入LLM API密钥）
nano backend/.env

# 3. 启动（Linux/Mac）
chmod +x deploy.sh
./deploy.sh

# 或Windows（进入项目目录）
.\deploy.bat
```

等待几秒钟后：
- **后端**: http://localhost:8000
- **前端**: http://localhost:5173
- **API文档**: http://localhost:8000/docs

### 使用Docker Compose

```bash
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

---

## 首次使用步骤

1. **访问http://localhost:5173**（或Railway提供的URL）

2. **进入 "公众号管理" 页面**

3. **添加公众号**
   - 输入公众号名称
   - 输入微信账号ID（如 `account@weixin`)
   - 点击添加

4. **等待爬虫运行**
   - 默认每天09:00自动爬取
   - 或进入 "任务状态" 页面点击 "立即执行任务"

5. **查看文章和摘要**
   - 进入 "文章流" 页面
   - 选择公众号和日期筛选
   - 点击 "显示摘要" 查看AI生成的摘要

---

## 关键配置

### LLM供应商选择

#### 百度文心千帆（推荐 ⭐⭐⭐⭐⭐）
```bash
LLM_PROVIDER=baidu
BAIDU_API_KEY=your-key
BAIDU_SECRET_KEY=your-secret
```
- 价格便宜 💰
- 中文支持好 🇨🇳
- 稳定可靠 ✅

#### OpenAI（高质量但贵）
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```
- 摘要质量最好 ⭐⭐⭐⭐⭐
- 价格较贵 💸
- 需要VPN 🔐

#### 阿里通义千问
```bash
LLM_PROVIDER=aliyun
ALIYUN_API_KEY=your-key
```
国内用户友好

### 爬虫配置

```bash
# 爬虫延迟（秒），越大越难被检测
CRAWL_DELAY_SECONDS=2

# 是否使用无头浏览器
HEADLESS_BROWSER=true

# 浏览器超时（秒）
BROWSER_TIMEOUT_SECONDS=30

# 定时爬虫时间
CRAWL_SCHEDULE_HOUR=9
CRAWL_SCHEDULE_MINUTE=0
```

---

## 常见问题

### Q: 爬虫获取失败，提示登录？
A: 微信有反爬虫机制，当前版本使用Playwright自动化爬取，需要：
   - 确保有有效的微信登录态
   - 定期更新User-Agent
   - 使用代理IP轮换（可选配置）
   - 等待几分钟后重试

### Q: LLM API调用失败？
A: 检查：
   - API Key是否正确
   - 账户余额是否充足
   - 网络连接是否正常
   - 查看日志: `docker-compose logs backend`

### Q: Railway部署没反应？
A: 
   - 检查构建日志：Railway Dashboard → Logs
   - 确保DATABASE_URL正确（Railway自动生成）
   - 检查环境变量完整性
   - 查看 Deployments 标签页

### Q: 前端无法连接后端？
A: 
   - 本地: 确保 `VITE_API_URL` 指向`http://localhost:8000/api/v1`
   - 云端: Railway自动代理，前端会自动连接
   - 检查浏览器DevTools → Network标签

### Q: 数据库表不存在？
A: 
   ```bash
   # 手动初始化
   docker-compose exec backend python -c \
     "from app.core.config import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

---

## 下一步操作

### 📚 深入学习
- 查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解生产部署细节
- 查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解代码结构和开发流程

### 🔧 自定义爬虫
- 修改 `backend/app/crawlers/wechat.py` 实现专有爬虫逻辑
- 添加反爬虫对策（代理、延迟、User-Agent轮换）
- 集成其他数据源（如RSS、API等）

### 🎨 美化前端
- 修改 `frontend/tailwind.config.js` 自定义主题色
- 在 `frontend/src/pages/` 添加新页面
- 集成数据看板和统计图表

### 🚀 扩展功能
- 添加用户认证和权限管理
- 集成更多LLM供应商
- 支持导出为PDF或Word
- 添加邮件订阅功能
- 集成知识库搜索

---

## 获取帮助

遇到问题？
1. 检查 [CONTRIBUTING.md](./CONTRIBUTING.md) 的"常见问题"部分
2. 查看应用日志找出错误信息
3. 提交Issue或PR

---

## 许可证

MIT - 自由使用和修改

---

**祝你使用愉快！** 🎉

如果觉得有帮助，请给项目点个Star ⭐
