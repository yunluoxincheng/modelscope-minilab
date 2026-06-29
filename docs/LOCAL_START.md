# 本地启动指南

## 1. 环境要求

- Python 3.10+
- PyTorch 2.x（CPU 或带 CUDA）
- Redis（可选；不装会自动降级为进程内限流）
- MySQL 8.x（可选；开发默认使用 SQLite）

## 2. 安装后端依赖

```bash
cd "E:/AllProjects/智能算法作业/ModelScope MiniLab/backend"
python -m venv .venv
source .venv/Scripts/activate      # Git Bash on Windows
# 或者 PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt   # 仅本地开发/测试
```

## 3. 配置环境变量

```bash
cp .env.example .env
```

本地开发推荐保持：

```dotenv
ENV=dev
DEBUG=true
DATABASE_URL=sqlite:///./minilab.db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=<生成一段 32 字节以上的随机字符串>
WECHAT_AUTH_MOCK=true
SERVICE_WINDOW_ENFORCE=false
CAT_DOG_ENSEMBLE_WEIGHTS=5:1:3
```

`WECHAT_AUTH_MOCK=true` 时，后端不会真的请求微信 `code2Session`，会把 `code` 直接当作 `openid`（前缀 `mock-`）。**仅用于本地开发，生产环境必须关闭**。

## 4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：

- 健康检查：[http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- OpenAPI 文档：[http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)

启动时数据库会自动 `create_all()`，并把 `cat-dog` 模型元数据写入 `ai_models` 表。

## 5. 启动小程序

1. 打开微信开发者工具。
2. 选择「导入项目」，目录指向 `miniapp/`。
3. 填写你的微信小程序 AppID（开发期可使用测试号）。
4. 修改 `miniapp/utils/config.js` 的 `API_BASE`，指向本地后端：

   ```js
   const API_BASE = 'http://127.0.0.1:8000/api';
   ```

5. 在「详情 → 本地设置」勾选「不校验合法域名…」，否则 `wx.request` 在开发工具里会被拦截。

## 6. 运行测试

```bash
cd backend
python -m pytest tests/ -v
```

测试默认使用临时 SQLite 数据库，不需要 MySQL/Redis 真实实例。
