# 生产部署指南

目标：把后端部署到一台云服务器（默认 CPU 推理），10:00-18:00 提供服务；微信小程序通过 HTTPS 调用。

## 1. 服务器准备

- 一台 Linux 云主机（推荐 Ubuntu 22.04 / 2C4G 以上）。
- 安装 Python 3.10+、MySQL 8.x、Redis 7.x。
- 准备 HTTPS 反向代理（Nginx + Let's Encrypt）。

## 2. 数据库初始化

```sql
CREATE DATABASE minilab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'minilab'@'%' IDENTIFIED BY '请改成强密码';
GRANT ALL PRIVILEGES ON minilab.* TO 'minilab'@'%';
FLUSH PRIVILEGES;
```

后端启动时会自动 `create_all()` 建表并 seed `cat-dog` 行。

## 3. 拉代码并准备模型权重

```bash
git clone <your-repo> /opt/minilab
cd /opt/minilab/backend
# 确保 checkpoints 已经存在于 ml_assets/cat_dog/checkpoints/
ls ml_assets/cat_dog/checkpoints/
# efficientnet_b0_v2.pth  efficientnet_b0_v3.pth  efficientnet_b0_v4.pth
```

> 三个 `efficientnet_b0_v*.pth` 必须存在，否则推理会失败。

## 4. 配置 .env（生产）

```dotenv
ENV=prod
DEBUG=false
DATABASE_URL=mysql+pymysql://minilab:强密码@127.0.0.1:3306/minilab?charset=utf8mb4
REDIS_URL=redis://127.0.0.1:6379/0
JWT_SECRET=<openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=168

WECHAT_AUTH_MOCK=false       # 生产必须关
WECHAT_APP_ID=<你的微信小程序 AppID>
WECHAT_APP_SECRET=<你的微信小程序 AppSecret>

MAX_UPLOAD_MB=5
ALLOWED_IMAGE_TYPES=image/jpeg,image/jpg,image/png,image/webp

CAT_DOG_ENSEMBLE_WEIGHTS=5:1:3
CAT_DOG_IMG_SIZE=256
CAT_DOG_THRESHOLD=0.5

SERVICE_WINDOW_ENFORCE=true
SERVICE_WINDOW_START=10:00
SERVICE_WINDOW_END=18:00

CORS_ALLOW_ORIGINS=https://your-domain.com
```

`.env` 文件权限设为 `600`，**不要提交到代码仓库**。

## 5. systemd 服务

`/etc/systemd/system/minilab.service`：

```ini
[Unit]
Description=ModelScope MiniLab API
After=network.target mysql.service redis.service

[Service]
WorkingDirectory=/opt/minilab/backend
EnvironmentFile=/opt/minilab/backend/.env
ExecStart=/opt/minilab/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=on-failure
RestartSec=3
User=minilab

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now minilab
sudo systemctl status minilab
```

## 6. Nginx 反向代理（HTTPS）

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate     /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 6m;     # 略大于 MAX_UPLOAD_MB

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

## 7. 微信合法域名配置

登录 [微信公众平台](https://mp.weixin.qq.com/) → 开发管理 → 开发设置 → 服务器域名：

- **request 合法域名**：`https://your-domain.com`
- **uploadFile 合法域名**：`https://your-domain.com`
- **downloadFile 合法域名**（如需要）：`https://your-domain.com`

修改 `miniapp/utils/config.js` 的 `API_BASE` 为 `https://your-domain.com/api` 后重新发版。

## 8. 服务时间

`SERVICE_WINDOW_ENFORCE=true` 时，超出 10:00-18:00 的请求会被拒绝并返回：

```json
{ "error": { "code": "SERVICE_UNAVAILABLE", "message": "服务暂不可用，请在开放时间内重试", "request_id": "..." } }
```

如需 7×24 运行，把 `SERVICE_WINDOW_ENFORCE` 改为 `false` 即可。

## 9. 升级与回滚

- 拉取新代码 → `sudo systemctl restart minilab`。
- 如果数据库 schema 变化（v2+），需要写 Alembic 迁移；当前 v1 直接 `create_all()`。
- PyTorch 模型权重更新只需替换 `ml_assets/cat_dog/checkpoints/` 下的文件后重启。

## 10. 监控与日志

- `journalctl -u minilab -f` 查看实时日志。
- 推荐接入 Sentry / 自建 Prometheus 采集 `/api/health`。
- 日志默认只记录 `request_id`、`model_id`、`latency_ms`、`status`；**不会**记录图片字节、Token、`session_key`。
