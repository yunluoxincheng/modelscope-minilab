# Web 前端（web/）

Vue 3 + Vite + Element Plus 实现的浏览器端界面，与微信小程序功能对齐：模型列表、上传图片推理、历史记录、账号体系。

- 路由：`/` 模型广场、`/models/:id` 实验台（上传预测）、`/history` 识别记录（需登录）、`/about` 关于、`/login` 登录/注册
- 登录：用户名 + 密码（`/api/auth/register`、`/api/auth/login`，与小程序的微信登录共用同一套 JWT 与用户表）
- 接口地址：默认同源 `/api`（开发时 Vite 代理到 `127.0.0.1:8000`，生产由 web 容器内的 nginx 反代到 `backend` 服务），可用 `VITE_API_BASE` 覆盖

## 本地开发

```bash
# 1) 起后端（见 docs/LOCAL_START.md）
cd backend
uvicorn app.main:app --reload --port 8000

# 2) 起前端（另开终端）
cd web
npm install
npm run dev        # http://localhost:5173，/api 自动代理到 8000
```

## 生产部署（Docker）

镜像由 GitHub Actions 自动构建多架构（amd64 + arm64）并推送：
`yunluoxincheng/modelscope-minilab-web:latest`（触发条件：push 到 `main` 且 `web/**` 有改动，也可手动 `workflow_dispatch`）。

`docker-compose.yml` 已包含 `web` 服务（默认 `8080` 端口，`.env` 里 `WEB_HTTP_PORT` 可改），
`docker compose pull && docker compose up -d` 即可一并部署。容器内 nginx 做：

1. SPA 静态资源托管 + history 路由回退（`try_files ... /index.html`）
2. `/api/` 反代到 compose 网络里的 `backend:8000`——**前端与接口同源，无需 CORS**

### 服务器 Nginx 配置

在原有 `server` 块（已有 `/api/` → 8000，小程序在用）里**加一条** `location /`：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    # ... ssl 证书配置不变 ...

    client_max_body_size 6m;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;   # 保持不变（小程序仍在用）
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 新增：Web 前端
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

两条 location 在同一 server 块 = 同一个 HTTPS 域名下同时服务网页和接口，
浏览器没有跨域问题；`/api/` 这条也可以删掉，由 web 容器代转。

### 首次上线清单

1. `./deploy.sh`（会同时拉起 backend / web / redis，并做健康检查）
2. 按上面改服务器 Nginx，`nginx -t && nginx -s reload`
3. 浏览器打开 `https://你的域名` → 注册账号 → 上传图片试一次识别

## 说明

- 密码使用 PBKDF2-SHA256（20 万次迭代 + 随机盐）哈希存储，登录接口按 IP 限流
- 用户名规则：3–32 位字母/数字/`_`/`-`；同一用户名全站唯一
- 老库无需手动迁移：后端启动时自动给 `users` 表补 `username` / `password_hash` 两列
- 登录颁发 JWT（默认 7 天有效），接口用法与微信登录完全一致（`Authorization: Bearer <token>`）
