# 开发指南

## 项目结构

```
wechat-summary-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI应用主文件
│   │   ├── core/
│   │   │   └── config.py        # 配置管理
│   │   ├── models/
│   │   │   ├── database.py      # SQLAlchemy ORM模型
│   │   │   └── schemas.py       # Pydantic数据验证模型
│   │   ├── api/
│   │   │   ├── accounts.py      # 公众号管理API
│   │   │   ├── articles.py      # 文章API
│   │   │   └── tasks.py         # 任务管理API
│   │   ├── crawlers/
│   │   │   └── wechat.py        # 爬虫模块
│   │   ├── summarizer/
│   │   │   ├── client.py        # LLM客户端
│   │   │   └── service.py       # 摘要生成服务
│   │   └── tasks/
│   │       └── scheduler.py     # APScheduler定时任务
│   ├── requirements.txt         # Python依赖
│   └── .env.example             # 环境变量示例
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React入口
│   │   ├── App.tsx              # 主应用组件
│   │   ├── index.css            # 全局样式
│   │   ├── components/          # 可复用组件
│   │   ├── pages/               # 页面组件
│   │   ├── hooks/               # 自定义Hook
│   │   └── utils/
│   │       └── api.ts           # API客户端
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── Dockerfile                   # 后端Docker镜像
├── frontend.Dockerfile          # 前端Docker镜像
├── docker-compose.yml           # 本地开发compose文件
├── nginx.conf                   # Nginx反向代理配置
├── railway.toml                 # Railway部署配置
├── deploy.sh                    # 部署脚本（Linux/Mac）
├── deploy.bat                   # 部署脚本（Windows）
├── README.md                    # 项目说明
├── DEPLOYMENT.md                # 部署指南
└── CONTRIBUTING.md              # 开发指南
```

## 本地开发环境搭建

### 前提条件
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (可选，可使用Docker)
- Docker & Docker Compose (推荐)

### 方式1: Docker Compose（推荐）

```bash
# 1. 准备环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 配置LLM API密钥等

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 访问应用
# 后端: http://localhost:8000
# 前端: http://localhost:5173
# API文档: http://localhost:8000/docs

# 5. 停止服务
docker-compose down
```

### 方式2: 本地开发（手动）

#### 后端设置

```bash
cd backend

# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和LLM密钥

# 4. 初始化数据库
python -c "from app.core.config import engine, Base; Base.metadata.create_all(bind=engine)"

# 5. 启动开发服务器
uvicorn app.main:app --reload

# 访问: http://localhost:8000
# API文档: http://localhost:8000/docs
```

#### 前端设置

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev

# 访问: http://localhost:5173
```

## 开发工作流

### 添加新的API端点

1. **定义Pydantic模型** (`app/models/schemas.py`)
   ```python
   class MyModelCreate(BaseModel):
       name: str
       description: Optional[str] = None
   ```

2. **定义ORM模型** (`app/models/database.py`)
   ```python
   class MyModel(Base):
       __tablename__ = "my_models"
       id = Column(Integer, primary_key=True)
       name = Column(String, index=True)
   ```

3. **创建API路由** (`app/api/my_routes.py`)
   ```python
   router = APIRouter(prefix="/myresources", tags=["myresource"])
   
   @router.get("")
   def list_resources(db: Session = Depends(get_db)):
       return db.query(MyModel).all()
   ```

4. **在主应用中注册路由** (`app/main.py`)
   ```python
   from app.api import my_routes
   app.include_router(my_routes.router, prefix=settings.api_v1_str)
   ```

### 添加新的前端页面

1. **创建页面组件** (`frontend/src/pages/MyPage.tsx`)
   ```typescript
   export const MyPage: React.FC = () => {
     return <div>My Page</div>
   }
   ```

2. **在路由中注册** (`frontend/src/App.tsx`)
   ```typescript
   <Route path="/mypage" element={<MyPage />} />
   ```

3. **在导航中添加链接** (`frontend/src/components/Navigation.tsx`)

### 修改爬虫逻辑

爬虫模块位于 `backend/app/crawlers/wechat.py`

主要修改的地方：
- `WechatCrawler.get_articles_list()` - 爬取文章列表
- `WechatCrawler.get_article_content()` - 爬取文章内容
- 反爬虫对策（User-Agent、延迟、代理等）

### 集成新的LLM供应商

1. **在 `app/summarizer/client.py` 中添加新的客户端类**
   ```python
   class MyLLMClient(LLMapiClient):
       async def summarize(self, text: str, max_length=None):
           # 实现摘要逻辑
           pass
   ```

2. **在 `create_summarizer()` 工厂函数中注册**
   ```python
   elif provider == "my_llm":
       return MyLLMClient(...)
   ```

3. **更新配置文件和环境变量**

## 数据库迁移

当修改ORM模型时，需要迁移数据库：

```bash
# 简单方式：重新创建表
docker-compose down
docker volume rm wechat-summary-app_postgres_data
docker-compose up -d

# 生产环境建议使用Alembic:
pip install alembic
alembic init migrations
# 按提示修改migrations文件
alembic upgrade head
```

## 测试

### 后端单元测试
```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/
```

### 前端测试
```bash
cd frontend
npm test
```

## 代码风格

### Python
- 使用 PEP 8 风格
- 使用 Black 格式化：`black app/`
- 使用 isort 组织导入：`isort app/`

```bash
pip install black isort
black backend/app
isort backend/app
```

### TypeScript/React
- 使用 ESLint
- 遵循 React Hooks 最佳实践
- 使用 Prettier 格式化

```bash
cd frontend
npm run lint
npm run format
```

## 调试

### 后端调试
```python
# 使用pdb
import pdb; pdb.set_trace()

# 或使用IDE调试器
# PyCharm / VS Code 内置调试工具
```

### 前端调试
- 使用浏览器DevTools
- VS Code Debugger配置（.vscode/launch.json）
- React DevTools浏览器扩展

## 常见任务

### 重新爬取所有文章
```bash
# 通过API手动触发
curl -X POST http://localhost:8000/api/v1/tasks/run-now

# 或修改APScheduler配置立即执行
```

### 清理旧数据
```bash
docker-compose exec backend python -c "
from app.core.config import SessionLocal
from app.models.database import CrawlLog
from datetime import datetime, timedelta

db = SessionLocal()
# 删除30天前的日志
old_logs = db.query(CrawlLog).filter(
    CrawlLog.run_at < datetime.now() - timedelta(days=30)
).delete()
db.commit()
print(f'已删除 {old_logs} 条旧日志')
"
```

### 备份数据库
```bash
# PostgreSQL备份
docker-compose exec postgres pg_dump \
    -U wechat_user wechat_summary > backup.sql

# 恢复备份
cat backup.sql | docker-compose exec -T postgres psql \
    -U wechat_user wechat_summary
```

## 性能优化建议

1. **使用Redis缓存**
   - 缓存热点文章列表
   - 缓存公众号信息

2. **数据库优化**
   - 为常用查询字段添加索引
   - 使用分批处理大量数据

3. **前端优化**
   - 启用虚拟滚动处理大列表
   - 使用TanStack Query进行智能缓存

4. **爬虫优化**
   - 实现请求去重
   - 使用并发爬取（asyncio）
   - 实现代理轮换

## 常见问题

**Q: 爬虫无法获取文章内容？**
A: 微信有强大的反爬虫机制，需要：
   - 使用真实浏览器（Playwright/Selenium）
   - 真实的微信登录态
   - IP轮换和User-Agent轮换
   - 处理验证码

**Q: LLM API调用太贵？**
A: 可以：
   - 切换到便宜的供应商（如百度文心价格较低）
   - 缓存已生成的摘要
   - 实现摘要的增量生成
   - 降低摘要长度要求

**Q: 数据库查询很慢？**
A: 检查：
   - 是否添加了适当的索引
   - 查询是否N+1问题
   - 是否需要分页
   - 考虑使用缓存

## 贡献代码

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 许可证

MIT License - 详见LICENSE文件
