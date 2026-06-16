# 迅捷后台管理系统 (Xunjie Admin Dashboard)

这是一个基于 **FastAPI (Python)** 后端和 **Vue 3 + Vite** 前端构建的现代化、高性能后台管理系统开发模板。

---

## 📂 项目结构说明

整个项目采用前后端分离的架构：

```text
xunjie/
├── app/                  # 后端 FastAPI 应用程序目录
│   ├── api/              # API 接口路由层
│   │   └── v1/           # API 版本 1 (endpoints 包含实际的业务控制器)
│   ├── core/             # 核心配置模块 (配置加载、数据库初始化、安全工具)
│   │   ├── config.py     # 动态配置载入模块 (支持多环境变量文件及Docker覆盖)
│   │   └── database.py   # SQLAlchemy 异步连接池与会话管理
│   ├── models/           # 数据库 ORM 模型定义目录
│   ├── schemas/          # Pydantic 数据校验与序列化模式目录
│   └── main.py           # FastAPI 实例初始化与全局中间件配置
├── web/                  # 前端 Vue 3 + TypeScript 应用程序目录
│   ├── src/              # 前端源码
│   │   ├── api/          # 接口请求层
│   │   ├── components/   # 公共组件
│   │   ├── layout/       # 基础布局页面
│   │   ├── router/       # Vue Router 路由配置
│   │   ├── store/        # Pinia 状态管理
│   │   └── views/        # 各业务页面组件 (login, dashboard 等)
│   ├── index.html        # 前端入口 HTML
│   ├── vite.config.ts    # Vite 配置文件
│   └── package.json      # 前端依赖配置
├── .env                  # 本地私有环境变量配置文件 (已在 .gitignore 中忽略)
├── .env.example          # 环境变量模板文件 (用于共享配置项结构)
├── requirements.txt      # 后端依赖项声明文件
└── run.py                # 后端应用本地启动入口脚本
```

---

## ⚙️ 配置文件与外部覆盖机制 (Docker 友好)

为了支持打包成 Docker 镜像后能够在多环境下无缝运行，项目的配置设计具备**外部覆盖**和**高灵活性**。

项目启动时会读取以下优先级递增的配置文件：
1. 本地 `.env`（默认加载，用于本地调试）
2. 项目根目录下的 `config.env`（存在时将覆盖 `.env`）
3. 环境变量 `CONFIG_PATH` 所指向的绝对路径文件（最优先，用于部署容器时挂载外部配置文件）
4. 环境变量（系统原生环境变量如 `DATABASE_URL`，具有最高优先级，将直接覆盖任何配置文件中的同名项）

### 1. 配置参数列表

在 `.env` 或 `config.env` 中支持配置以下核心参数：

| 参数名称 | 默认值/示例 | 说明 |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `迅捷后台管理系统` | 系统名称 |
| `API_V1_STR` | `/api/v1` | 接口前缀路径 |
| `SECRET_KEY` | `supersecretkeyreplaceinproduction` | JWT 加密密钥（生产环境必须替换） |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | JWT Token 有效期（分钟） |
| `DATABASE_URL` | `mysql+aiomysql://root:666666@localhost:3306/fast_db` | 数据库连接字符串，支持异步 MySQL (`aiomysql`) |
| `ALGORITHM` | `HS256` | JWT 签发签名算法 |
| `BACKEND_CORS_ORIGINS` | `http://localhost,http://localhost:5173,http://localhost:8000` | 跨域允许的来源列表（支持逗号分隔或 JSON 数组） |
| `HOST` | `127.0.0.1` | 本地服务监听地址（Docker 部署时设为 `0.0.0.0`） |
| `PORT` | `8000` | 本地服务监听端口 |
| `RELOAD` | `True` | 是否开启热重载（生产/Docker 环境建议为 `False`） |

### 2. Docker 环境下如何进行配置替换

#### 方法 A：通过挂载外部 `.env` 文件 (推荐)
无需重新构建镜像，只需将您的外部配置文件挂载至容器内的特定路径，并通过设置 `CONFIG_PATH` 告诉容器读取它。

```bash
docker run -d \
  -p 8000:8000 \
  -v /opt/xunjie/my_config.env:/app/config.env \
  -e CONFIG_PATH=/app/config.env \
  --name xunjie-backend \
  xunjie-backend-image
```

#### 方法 B：通过 -e 参数直接覆盖
如果只需要修改数据库连接地址，也可以直接在启动命令中通过环境变量指定：

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://user:pwd@prod-mysql:3306/fast_db" \
  -e HOST="0.0.0.0" \
  -e RELOAD="False" \
  --name xunjie-backend \
  xunjie-backend-image
```

---

## 🚀 本地开发与运行指南

### 1. 后端 (FastAPI)

1. **创建并激活虚拟环境**：
   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
3. **数据库准备**：
   请在您的本地 MySQL 中创建名为 `fast_db` 的数据库，并配置 `.env` 中的 `DATABASE_URL`。
4. **启动服务**：
   ```bash
   python run.py
   ```
   后端服务启动后，可以通过访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 查看 Swagger 交互式 API 文档。

### 2. 前端 (Vue 3 + Vite)

1. **进入前端目录**：
   ```bash
   cd web
   ```
2. **安装依赖**：
   ```bash
   npm install
   ```
3. **启动开发服务器**：
   ```bash
   npm run dev
   ```
   前端服务将启动在 [http://localhost:5173](http://localhost:5173)。
