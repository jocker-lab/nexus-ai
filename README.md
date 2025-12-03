# Nexus AI

基于 LangGraph 的多智能体 AI 系统，用于研究分析和报告生成。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                   (Next.js + React)                          │
│                     localhost:3000                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/SSE
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend API                              │
│                  (FastAPI + LangGraph)                       │
│                     localhost:8000                           │
└───────┬─────────────────┬─────────────────┬─────────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │  MySQL  │      │  MinIO  │      │   LLM   │
   │  :3306  │      │  :9000  │      │   API   │
   └─────────┘      └─────────┘      └─────────┘
```

## 环境要求

- **Python**: 3.12+
- **Node.js**: 18+
- **MySQL**: 8.0+
- **MinIO**: 最新版（可选，用于文件存储）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/nexus-ai.git
cd nexus-ai
```

### 2. 后端配置

#### 2.1 创建 Python 虚拟环境

```bash
# 使用 conda
conda create -n nexus-ai python=3.12
conda activate nexus-ai

# 或使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

#### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.3 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入实际配置
```

**.env 主要配置项：**

```bash
# LangSmith 配置（可选，用于调试追踪）
LANGSMITH_PROJECT=nexus-ai
LANGSMITH_API_KEY=your_langsmith_api_key

# LLM API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_API_KEY=your_openai_api_key

# 搜索 API Keys
TAVILY_API_KEY=your_tavily_api_key

# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/nexus_ai?charset=utf8mb4

# MinIO 配置（可选）
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=nexus-reports
```

#### 2.4 配置 LLM 参数

编辑 `app/config/config.yaml`：

```yaml
# 大模型参数配置
model_params:
  model: "gpt-4o"                    # 或其他支持的模型
  openai_api_base: "https://api.openai.com/v1"  # API 地址
  max_tokens: 8192
  temperature: 0.7
```

#### 2.5 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE nexus_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行数据库迁移
cd migrations
alembic upgrade head
cd ..
```

#### 2.6 启动后端服务

```bash
# 开发模式
uvicorn main:app --reload --port 8000

# 或使用启动脚本
./start.sh
```

后端服务将在 http://localhost:8000 启动。

API 文档: http://localhost:8000/docs

---

### 3. 前端配置

#### 3.1 进入前端目录

```bash
cd web
```

#### 3.2 安装依赖

```bash
npm install
# 或
pnpm install
```

#### 3.3 配置环境变量

```bash
# 复制示例配置
cp .env.example .env.local

# 编辑配置（如需修改后端地址）
```

**.env.local 配置：**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 3.4 启动前端服务

```bash
# 开发模式
npm run dev

# 生产构建
npm run build
npm run start
```

前端服务将在 http://localhost:3000 启动。

---

### 4. MinIO 配置（可选）

如需使用文件存储功能：

```bash
# Docker 启动 MinIO
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```

MinIO 控制台: http://localhost:9001

---

## 目录结构

```
nexus-ai/
├── app/                    # 后端应用
│   ├── agents/             # AI Agent 实现
│   │   ├── core/           # 核心 Agent（Publisher, Research 等）
│   │   ├── prompts/        # Prompt 模板
│   │   └── schemas/        # 数据模型
│   ├── api/                # API 端点
│   ├── auth/               # 认证模块
│   ├── config/             # 配置文件
│   ├── curd/               # 数据库操作
│   ├── database/           # 数据库连接
│   └── models/             # ORM 模型
├── docker/                 # Docker 配置
├── logs/                   # 日志目录
├── migrations/             # 数据库迁移
├── test/                   # 测试文件
├── web/                    # Next.js 前端
│   ├── app/                # 页面和路由
│   ├── components/         # React 组件
│   └── lib/                # 工具库
├── main.py                 # FastAPI 入口
├── fastapi_sse_server_v4.py  # SSE 流式服务（开发测试用）
└── requirements.txt        # Python 依赖
```

---

## 开发测试

### Mock SSE 服务器

用于前端开发测试，节省 LLM tokens：

```bash
# 启动 Mock 服务器
cd test
python mock_sse_server.py
```

Mock 服务器在 http://localhost:8001 启动。

使用 `test/frontend_v4_mock.html` 进行前端测试。

### 运行测试

```bash
# 运行所有测试
pytest test/

# 运行特定测试
pytest test/test.py
```

---

## 常见问题

### 1. 数据库连接失败

- 检查 MySQL 服务是否启动
- 确认 `DATABASE_URL` 配置正确
- 确保数据库字符集为 `utf8mb4`

### 2. LLM API 调用失败

- 检查 API Key 是否正确配置
- 确认 `openai_api_base` 地址可访问
- 查看 `logs/` 目录下的错误日志

### 3. 前端连接后端失败

- 确认后端服务已启动
- 检查 `NEXT_PUBLIC_API_URL` 配置
- 确认 CORS 配置允许前端域名

---

## 生产部署

### Docker 部署

```bash
# 构建镜像
docker build -t nexus-ai -f docker/Dockerfile .

# 运行容器
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  nexus-ai
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # SSE 流式接口
    location /api/chat {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
}
```

---

## 贡献者

- Sean Xiao
- Claude (AI Assistant)

## License

MIT License
