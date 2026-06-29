# ModelScope MiniLab / 智模工坊

一个个人作品集风格的 AI 模型展示小程序，目前内置 **猫狗图像二分类** 模型（EfficientNet-B0 v2/v3/v4 加权 5:1:3 集成）。架构按"可扩展模型注册表 + 通用推理 API"的方式设计，未来加新模型只需要新增一个 predictor 模块和一条注册元数据。

- 前端：微信原生小程序（`miniapp/`）
- 后端：FastAPI + PyTorch（`backend/`）
- 数据库：MySQL 8.x（开发可用 SQLite）
- 限流：Redis（无 Redis 时自动回退到进程内限流）

## 目录结构

```
ModelScope MiniLab/
├── miniapp/                       微信小程序源码
│   ├── app.js / app.json / app.wxss
│   ├── pages/                     index / model-detail / history / about / login
│   └── utils/                     config / auth / request / api
├── backend/
│   ├── app/
│   │   ├── main.py                FastAPI 入口
│   │   ├── api/                   health / auth / models_api / predictions / deps
│   │   ├── core/                  settings / errors / security / rate_limit / logging
│   │   ├── db/                    session / models / repositories / bootstrap / seed
│   │   ├── models_registry/       base / entries / registry
│   │   └── predictors/            base / cat_dog / factory
│   ├── ml_assets/cat_dog/         EfficientNet-B0 模型定义 + checkpoint 拷贝
│   ├── tests/                     pytest 集成测试
│   ├── requirements.txt
│   └── .env.example
├── docs/                          部署、API 样例、小程序配置
└── goals/ai-model-miniapp-platform/GOAL.md
```

## 快速开始

详见 [docs/LOCAL_START.md](docs/LOCAL_START.md)。最简流程：

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

打开 [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs) 查看交互式 API 文档。

小程序部分：在微信开发者工具中导入 `miniapp/` 目录即可预览。

## 生产部署（Docker）

镜像由 GitHub Actions 自动构建多架构并推送到 Docker Hub；服务器部署**只需要两个文件**（`docker-compose.yml` + `.env`），不需要源码。

| 项 | 值 |
|---|---|
| GitHub 仓库 | https://github.com/yunluoxincheng/modelscope-minilab |
| Docker 镜像 | `yunluoxincheng/modelscope-minilab-backend`（tags：`1.0.0` / `latest`） |
| 支持架构 | linux/amd64 + linux/arm64（自动匹配服务器架构） |
| CI 触发 | push 到 `main` 自动重建；也可在 Actions 页手动 `workflow_dispatch` |

**三步部署**（完整版见 [docs/DOCKER_DEPLOY.md](docs/DOCKER_DEPLOY.md)）：

```bash
# 1) 服务器上放好 docker-compose.yml，配 .env（密钥由环境变量注入）
cp docker-compose.env.example .env
#   必改：JWT_SECRET（用 openssl rand -hex 32 生成）、WECHAT_APP_SECRET；
#         生产把 WECHAT_AUTH_MOCK=false
vim .env

# 2) 拉镜像 + 启动（backend + redis）
docker compose pull
docker compose up -d

# 3) 验证
curl http://127.0.0.1:8000/api/health     # → {"status":"ok","service":"ModelScope MiniLab API",...}
```

上线前还需完成：Nginx + HTTPS 反代（微信小程序的 `wx.uploadFile` 要求 HTTPS）、微信公众平台配置 request / uploadFile 合法域名、小程序 `miniapp/utils/config.js` 改成线上 `https://你的域名/api`。详见 [docs/DOCKER_DEPLOY.md](docs/DOCKER_DEPLOY.md)。

## 文档

- [docs/LOCAL_START.md](docs/LOCAL_START.md) — 本地开发启动
- [docs/API_SAMPLES.md](docs/API_SAMPLES.md) — 接口调用示例
- [docs/MINIAPP_SETUP.md](docs/MINIAPP_SETUP.md) — 小程序配置
- [docs/DOCKER_DEPLOY.md](docs/DOCKER_DEPLOY.md) — 服务器 docker-compose 部署（推荐）
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — 裸机生产部署 / 微信合法域名 / 服务时间
- [backend/tests/](backend/tests/) — pytest 自动化测试

## 测试

```bash
cd backend
python -m pytest tests/
```

当前覆盖：health / 模型列表 / 模型详情 / 未登录拦截 / 缺文件 / 不支持类型 / 超大文件 / 非法图片 / 成功预测 / 历史 / 登录幂等 / 限流。
