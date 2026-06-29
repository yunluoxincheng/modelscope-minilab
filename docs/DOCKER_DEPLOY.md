# 服务器部署（docker-compose）

镜像已由 GitHub Actions 构建并推送到 Docker Hub，多架构（amd64 + arm64）：
`yunluoxincheng/modelscope-minilab-backend`，tags：`1.0.0` / `latest`。

## 一键部署（推荐）

用仓库自带的 `deploy.sh`：自动检查环境 → 校验 `.env` → 拉镜像 → 启动 → 健康检查。服务器上**只需脚本 + `.env` 两个文件**（`docker-compose.yml` 缺失时会自动从 GitHub 拉）。

```bash
mkdir -p ~/minilab && cd ~/minilab

# 拉部署脚本（国内服务器建议用 jsDelivr 源；raw.githubusercontent.com 常被墙）
curl -fsSL https://cdn.jsdelivr.net/gh/yunluoxincheng/modelscope-minilab@main/deploy.sh -o deploy.sh
chmod +x deploy.sh          # 必做！curl 下载不带执行位，不 chmod 会报 sudo: ./deploy.sh: command not found
head -1 deploy.sh           # 验证下载对了：第一行必须是 #!/usr/bin/env bash

# 把你填好密钥的 .env 上传到这里（JWT_SECRET / WECHAT_APP_ID / WECHAT_APP_SECRET 等）
#   scp .env user@server:~/minilab/

./deploy.sh        # 首次部署；跑完会自检 /api/health 并打印 HTTPS / 合法域名提醒
```

常用命令：

| 命令 | 作用 |
|---|---|
| `./deploy.sh` | 部署/更新（拉镜像 + 启动 + 健康检查） |
| `./deploy.sh mysql` | 同时启用 MySQL |
| `./deploy.sh status` / `logs` / `restart` / `down` / `health` | 运维 |
| `./deploy.sh --no-pull` | 用本地已有镜像（离线 / 锁版本） |

脚本不会打印任何密钥值；生产环境（`ENV=prod`）下若 `.env` 里 `WECHAT_AUTH_MOCK=true` 会**拒绝启动**。

> 下面是不用脚本的手动分步说明。

## 0. 前置条件

服务器上需要：
- Docker Engine（含 `docker compose` v2 插件）
- 一份 `docker-compose.yml` 和 `.env`（只需这两个文件，不需要源码）
- 一个 HTTPS 域名（微信小程序的 `wx.request` / `wx.uploadFile` 要求 HTTPS）

## 1. 准备部署目录

在服务器上：

```bash
mkdir -p ~/minilab && cd ~/minilab
# 把本地的 docker-compose.yml 上传到服务器（scp 或直接复制内容）
# 例如：scp docker-compose.yml user@server:~/minilab/
```

## 2. 配置 .env

```bash
cp docker-compose.env.example .env   # 如果连模板也上传了；否则按 docker-compose.env.example 手写一份
vim .env
```

**生产必须改这几项**：

```dotenv
ENV=prod
DEBUG=false

# SQLite 默认落到 docker 卷里，重启不丢；想用 MySQL 见下方"启用 MySQL"
DATABASE_URL=sqlite:///./data/minilab.db

# 生成强随机串：openssl rand -hex 32
JWT_SECRET=<粘贴上面命令的输出>

# 微信登录（生产必须关 mock，填真实 AppSecret）
WECHAT_AUTH_MOCK=false
WECHAT_APP_ID=<你的微信小程序 AppID，微信公众平台 → 开发设置>
WECHAT_APP_SECRET=<微信公众平台 → 开发设置里的 AppSecret>

# 10:00-18:00 开放；想 7×24 改 false
SERVICE_WINDOW_ENFORCE=true
```

## 3. 启动

```bash
docker compose pull          # 拉镜像（amd64/arm64 自动匹配服务器架构）
docker compose up -d         # 启动 backend + redis
docker compose logs -f backend   # 看启动日志，出现 "Application startup complete" 即 OK
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/health
# {"status":"ok","service":"ModelScope MiniLab API", ...}
```

## 4. Nginx + HTTPS（微信必需）

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    ssl_certificate     /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 6m;        # 略大于 5MB 上传上限

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

证书用 Let's Encrypt（`certbot --nginx -d your-domain.com`）。

## 5. 微信合法域名

[微信公众平台](https://mp.weixin.qq.com/) → 开发管理 → 开发设置 → 服务器域名：
- request 合法域名：`https://your-domain.com`
- uploadFile 合法域名：`https://your-domain.com`

然后改 `miniapp/utils/config.js`：
```js
const API_BASE = 'https://your-domain.com/api';
```
重新发布小程序。

## 6. （可选）启用 MySQL

```bash
docker compose --profile mysql up -d
```

并把 `.env` 里的 `DATABASE_URL` 改为：
```dotenv
DATABASE_URL=mysql+pymysql://minilab:你的MYSQL_PASSWORD@mysql:3306/minilab?charset=utf8mb4
```
（`MYSQL_PASSWORD` 要和 `.env` 里的 `MYSQL_PASSWORD` 一致；`MYSQL_DATABASE`、`MYSQL_USER` 同理）

## 7. 更新镜像

后续代码改动 push 到 GitHub，Actions 自动构建新镜像（`:latest` + `:1.0.0`）。服务器更新：

```bash
docker compose pull
docker compose up -d
```

## 8. 常用运维命令

```bash
docker compose ps                 # 查看服务状态
docker compose restart backend    # 重启后端
docker compose logs --tail=200 backend
docker compose down               # 停止（数据卷保留）
docker compose down -v            # 停止并删除数据（慎用，会丢历史记录）
```

## 9. 排错

| 现象 | 排查 |
|------|------|
| `docker compose up` 后 backend 一直 unhealthy | `docker compose logs backend`，常见是 `.env` 里 JWT_SECRET 没填或端口被占 |
| 微信小程序请求失败 | 先确认域名 HTTPS、合法域名已配、`API_BASE` 已改 |
| 预测返回 503 | 服务时间窗口外（默认 10:00-18:00），或在 `.env` 设 `SERVICE_WINDOW_ENFORCE=false` |
| 微信登录失败 | 生产环境 `WECHAT_AUTH_MOCK` 必须为 `false`，且 AppSecret 正确 |
