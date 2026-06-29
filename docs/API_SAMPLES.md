# API 调用样例

所有路径前缀为 `/api`。错误响应统一为：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "用户可理解的错误信息",
    "request_id": "..."
  }
}
```

## GET /api/health

```bash
curl http://127.0.0.1:8000/api/health
```

```json
{
  "status": "ok",
  "service": "ModelScope MiniLab API",
  "time": "2026-06-18T13:00:00+00:00",
  "env": "dev"
}
```

## POST /api/auth/wechat-login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/wechat-login \
  -H "Content-Type: application/json" \
  -d '{"code": "dev-fake-code"}'
```

```json
{
  "token": "eyJ...",
  "user": {
    "id": 1,
    "openid_masked": "moc***code",
    "nickname": null,
    "avatar_url": null
  }
}
```

> 生产环境 `WECHAT_AUTH_MOCK=false` 时，后端会真的请求微信 `code2Session`，需要正确配置 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`。

## GET /api/models

```bash
curl http://127.0.0.1:8000/api/models
```

```json
{
  "items": [
    {
      "model_id": "cat-dog",
      "name": "猫狗图像二分类",
      "name_en": "Cat-Dog Classifier",
      "description": "上传一张猫或狗的照片，模型判断它属于哪一类。",
      "task_type": "image_classification",
      "input_type": "image",
      "output_type": "classification",
      "enabled": true,
      "cover_url": null
    }
  ],
  "total": 1
}
```

## GET /api/models/{model_id}

```bash
curl http://127.0.0.1:8000/api/models/cat-dog
```

```json
{
  "model_id": "cat-dog",
  "name": "猫狗图像二分类",
  "name_en": "Cat-Dog Classifier",
  "description": "...",
  "task_type": "image_classification",
  "input_type": "image",
  "output_type": "classification",
  "enabled": true,
  "cover_url": null,
  "supported_file_types": ["image/jpeg", "image/jpg", "image/png", "image/webp"],
  "max_upload_mb": 5,
  "capabilities": ["predict"]
}
```

## POST /api/models/{model_id}/predict

```bash
TOKEN="eyJ..."   # 从 wechat-login 拿到
curl -X POST http://127.0.0.1:8000/api/models/cat-dog/predict \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/cat.jpg"
```

成功：

```json
{
  "request_id": "5b3a...",
  "model_id": "cat-dog",
  "label": "cat",
  "label_cn": "猫",
  "confidence": 0.912,
  "probabilities": { "cat": 0.912, "dog": 0.088 },
  "latency_ms": 142,
  "created_at": "2026-06-18T13:01:42Z"
}
```

未登录（401）：

```json
{ "error": { "code": "UNAUTHORIZED", "message": "请先登录", "request_id": "..." } }
```

超大文件（400）：

```json
{ "error": { "code": "FILE_TOO_LARGE", "message": "图片不能超过 5MB", "request_id": "..." } }
```

不支持类型（400）：

```json
{ "error": { "code": "UNSUPPORTED_FILE_TYPE", "message": "仅支持 JPG、PNG、WEBP 图片", "request_id": "..." } }
```

## GET /api/predictions/history

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/predictions/history?page=1&page_size=20"
```

```json
{
  "items": [
    {
      "id": 1,
      "request_id": "5b3a...",
      "model_id": "cat-dog",
      "result_label": "cat",
      "result_label_cn": "猫",
      "confidence": 0.912,
      "probabilities": { "cat": 0.912, "dog": 0.088 },
      "latency_ms": 142,
      "status": "success",
      "created_at": "2026-06-18T13:01:42Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```
