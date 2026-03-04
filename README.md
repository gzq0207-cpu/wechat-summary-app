# 微信公众号文章聚合摘要系统

自动爬取多个微信公众号每日文章，使用LLM API生成高质量摘要，通过网页展示文章时间线和分类信息。

## 🏗️ 架构

- **后端**: FastAPI + PostgreSQL + Playwright + APScheduler
- **前端**: React 18 + TypeScript + Tailwind CSS
- **部署**: Docker + Railway/阿里云
- **摘要生成**: 百度文心千帆 API / Claude API

## 📋 功能清单

- [x] 自动爬取微信公众号历史文章
- [x] 每日定时任务自动更新文章
- [x] LLM高质量摘要生成
- [x] Web前端展示文章流和摘要
- [x] 公众号管理（添加/删除）
- [x] 文章搜索和分类筛选
- [x] 爬虫任务监控和日志

## 🚀 快速开始

### 本地开发

#### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # 或 venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # 配置环境变量
uvicorn app.main:app --reload
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

### 云端部署

#### Railway
1. 推送代码到GitHub
2. 在Railway Dashboard创建新项目
3. 连接GitHub仓库
4. 配置环境变量（DATABASE_URL, LLM 密钥等）
5. 自动部署

#### 阿里云ECS
```bash
docker-compose up -d
```

## 📦 环境变量

```ini
# 数据库 (Railway自动提供 DATABASE_URL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# LLM API
LLM_PROVIDER=baidu|openai|aliyun
BAIDU_API_KEY=your_key
BAIDU_SECRET_KEY=your_secret

# 爬虫配置
WECHAT_LOGIN_USERNAME=your_wechat_username
WECHAT_LOGIN_PASSWORD=your_password
CRAWL_DELAY_SECONDS=3
HEADLESS_BROWSER=true

# 应用配置
FASTAPI_ENV=production
SECRET_KEY=your_secret_key
```

## 📚 API文档

启动后端后访问: http://localhost:8000/docs

### 主要端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/accounts` | 获取已追踪公众号列表 |
| POST | `/api/accounts` | 添加新公众号 |
| GET | `/api/articles` | 获取文章列表（支持筛选） |
| GET | `/api/articles/{id}` | 获取文章详情 |
| GET | `/api/articles/{id}/summary` | 获取文章摘要 |
| POST | `/api/tasks/run-now` | 手动触发爬虫任务 |
| GET | `/api/tasks/status` | 查看任务执行状态 |

## 🧪 测试

```bash
cd backend
pytest tests/
```

## 📄 许可证

MIT

## ⚠️ 法律声明

本应用仅供个人学习和研究使用，商业用途需与微信官方合作。
