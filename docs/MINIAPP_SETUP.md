# 微信小程序配置

## 1. 导入项目

1. 打开微信开发者工具。
2. 选择「导入项目」，目录选择 `miniapp/`。
3. AppID 填写你的微信小程序 AppID。
4. 修改 `miniapp/project.config.json` 的 `appid` 字段为正式 AppID。

## 2. 修改后端地址

打开 `miniapp/utils/config.js`：

```js
const API_BASE = 'http://127.0.0.1:8000/api';   // 本地开发
```

部署到生产后改为：

```js
const API_BASE = 'https://your-domain.com/api';
```

## 3. 本地调试

- 详情 → 本地设置 → 勾选 **「不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书」**，否则开发工具里 `wx.request` 会被拦截。
- 真机预览：手机与电脑处于同一网络，把 `API_BASE` 改为 `http://<电脑局域网IP>:8000/api`。

## 4. 页面结构

| 路径 | 用途 |
|------|------|
| `pages/index/index` | 首页：模型卡片列表 |
| `pages/model-detail/model-detail` | 模型详情 + 上传识别 |
| `pages/history/history` | 当前用户的历史记录 |
| `pages/about/about` | 关于（项目介绍） |
| `pages/login/login` | 微信一键登录 |

## 5. 上传识别流程

1. 首页拉 `GET /api/models`，渲染卡片。
2. 点击 cat-dog 卡片 → 进入详情。
3. 点「拍照 / 选择图片」，调起 `wx.chooseMedia`。
4. 前端做扩展名 + 大小校验。
5. 若未登录，跳转登录页（`pages/login/login`）。
6. 调 `wx.uploadFile` POST 到 `/api/models/cat-dog/predict`，字段名 `file`。
7. 推理期间按钮显示「识别中」。
8. 成功后页面正中只显示 `label_cn`（`猫` 或 `狗`），下方副位显示置信度。
9. 跳转「历史」可看到刚刚的记录。

## 6. 小程序登录态

- Token 存在 `wx.getStorageSync('minilab_token')`。
- `utils/auth.js` 提供 `getToken / setToken / clearToken / ensureLogin` 等工具。
- `utils/request.js` 自动给每个请求注入 `Authorization: Bearer <token>`。
