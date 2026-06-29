# Goal: Implement ModelScope MiniLab / 智模工坊 as an extensible AI model showcase mini-program platform

Do not stop until all acceptance criteria are met. This Goal is intended for Codex, Claude Code, or another coding Agent to implement directly. The previous instruction "only need Goal" applied only to the Goal-writing step, not to the coding Agent that receives this file.

## 1. Project Background

- Project name:
  - English: ModelScope MiniLab
  - Chinese: 智模工坊
- Project type: WeChat mini-program + backend AI inference service.
- Product positioning: personal portfolio showcase first, but designed to be stable enough for ordinary users to use long term.
- Tech stack:
  - Frontend: WeChat native mini-program.
  - Backend recommendation: Python FastAPI inference service.
  - Database recommendation: MySQL 8.x for user profile, model metadata, and prediction history.
  - Middleware recommendation: Redis for rate limiting and optional short-lived cache.
  - Model runtime: PyTorch on CPU first, with automatic CUDA support only if a future server has GPU.
  - Deployment: cloud server, normally available daily from 10:00 to 18:00.
- Existing capability:
  - A completed cat-dog classification project exists at `dogsAndcatsSort/`.
  - The first production model module should be cat-dog image classification.
  - The best strict-independent model is EfficientNet-B0 v2/v3/v4 weighted ensemble with weights 5:1:3.
  - Existing cat-dog assets include `model.py` and checkpoints:
    - `models/from_scratch/efficientnet_b0_v2.pth`
    - `models/from_scratch/efficientnet_b0_v3.pth`
    - `models/from_scratch/efficientnet_b0_v4.pth`

## 2. Objective

Implement an extensible AI model showcase platform so that public users can open a WeChat mini-program, view available AI model cards, choose a model, upload or capture an image, receive a prediction result from the backend model service, and later review their own prediction history after WeChat login.

The cat-dog classifier is only the first usable model module. The architecture must allow future models with different input and output formats to be added without rewriting the whole mini-program or backend.

## 3. Scope

Included:

1. Create a WeChat native mini-program structure for ModelScope MiniLab / 智模工坊.
2. Create an extensible backend API structure for model metadata and model inference.
3. Implement WeChat login and bind users to `openid`.
4. Implement a model card list as the mini-program home page.
5. Implement a model detail page with a user-facing prediction entry.
6. Implement the cat-dog image classification module as the first model.
7. Implement image upload prediction through `POST /api/models/{model_id}/predict`.
8. Return structured inference data from the backend, while the mini-program initially displays only the Chinese predicted label.
9. Save prediction history metadata for logged-in users.
10. Add basic rate limiting to prevent abusive requests.
11. Add backend validation for file type and file size, with 5 MB maximum image upload size.
12. Provide local and production deployment instructions.
13. Provide API test samples and manual mini-program verification steps.

Excluded from the first implementation iteration:

1. Long-term storage of uploaded original images. For v1, do not persist uploaded image files by default.
2. Admin console for managing models.
3. User-facing detailed model metrics, dataset details, training logs, or leakage notes.
4. Payment, subscription, membership, or quota purchase features.
5. Object detection, segmentation, OCR, text generation, or multimodal models unless they are added later through the extension interface.
6. Push notifications.
7. Social sharing leaderboard or public gallery.
8. Fully automated 24-hour operations. The target server window is 10:00-18:00 unless the deployment environment changes.

## 4. Relevant Directories

Recommended new project root:

- `E:/AllProjects/智能算法作业/ModelScope MiniLab/`

Recommended directory layout:

- `miniapp/`: WeChat native mini-program source.
- `backend/`: FastAPI backend service.
- `backend/app/`: backend application package.
- `backend/app/api/`: API route modules.
- `backend/app/core/`: config, security, rate limiting, startup hooks.
- `backend/app/db/`: database session, models, migrations, repositories.
- `backend/app/models_registry/`: model registry and metadata definitions.
- `backend/app/predictors/`: model-specific predictor modules.
- `backend/app/predictors/cat_dog.py`: first cat-dog predictor.
- `backend/ml_assets/cat_dog/`: copied cat-dog model definition and checkpoints needed for inference.
- `backend/tests/`: backend tests.
- `docs/`: deployment notes, API samples, and mini-program setup instructions.
- `goals/ai-model-miniapp-platform/GOAL.md`: this Goal.

Useful source project:

- `E:/AllProjects/智能算法作业/dogsAndcatsSort/`

Do not modify unless necessary:

- Do not modify the original training dataset under `dogsAndcatsSort/dataset/`.
- Do not retrain models as part of this Goal.
- Do not delete, move, or overwrite original checkpoints in `dogsAndcatsSort/models/`.
- Do not change the original training report unless separately requested.

## 5. Business Rules

1. The platform name should be:
   - English: ModelScope MiniLab
   - Chinese: 智模工坊
2. The mini-program home page must show a list of model cards, not jump directly into cat-dog classification.
3. Each model must be represented by metadata, including `model_id`, display name, task type, input type, output type, enabled status, and API capability.
4. The cat-dog model must have `model_id = "cat-dog"`.
5. The first cat-dog predictor should use EfficientNet-B0 v2/v3/v4 weighted ensemble with weights 5:1:3 by default.
6. The backend may provide a future configuration switch for fast mode using only EfficientNet-B0 v2, but the default mode must be the high-accuracy ensemble.
7. Users do not need to see detailed model internals in v1.
8. The mini-program result UI should show only the Chinese predicted class for the first version, for example `猫` or `狗`.
9. The backend response should still include useful diagnostic fields such as `model_id`, `label`, `label_cn`, `confidence`, `probabilities`, `latency_ms`, and `request_id`.
10. Prediction history should be saved for logged-in users, but original uploaded images should not be persisted by default in v1.
11. If the user is not logged in, the mini-program may still show model cards, but prediction should require login.
12. Upload size limit is 5 MB.
13. Supported image formats in v1: JPG, JPEG, PNG, and WEBP.
14. The system should be extensible enough to add future image models without modifying the existing cat-dog predictor logic.

## 6. Frontend Requirements

- Frontend stack: WeChat native mini-program.
- App name displayed to users: 智模工坊.
- Suggested pages:
  1. `pages/index/index`: model card list home page.
  2. `pages/model-detail/model-detail`: model detail and prediction entry.
  3. `pages/history/history`: current user's prediction history.
  4. `pages/about/about`: project and author introduction.
  5. `pages/login/login` or login modal/component: WeChat login flow.

User interaction flow:

1. User opens mini-program.
2. Home page calls `GET /api/models` and displays enabled models as cards.
3. User taps the cat-dog model card.
4. Model detail page shows the model name, short description, supported input type, and an upload/camera action.
5. If user is not logged in, prompt WeChat login before prediction.
6. User chooses an image from album or camera.
7. Mini-program validates basic file information when available.
8. Mini-program calls `wx.uploadFile` to `POST /api/models/cat-dog/predict`.
9. During upload and inference, show a loading state.
10. On success, display only the predicted Chinese label in the primary result area.
11. Optionally show confidence in a secondary area only if the UI design has room; do not make it the main focus.
12. User can navigate to history page and see previous prediction records.

UI requirements:

1. Home page should be a model card list suitable for future expansion.
2. Cat-dog card should be the first enabled card.
3. Disabled or future models may appear as "敬请期待" only if intentionally configured.
4. Keep UI simple, clear, and portfolio-friendly.
5. Do not expose training data leakage details to normal users in v1.
6. Use user-facing Chinese text by default.

Frontend state handling:

- Loading state:
  - Model list loading: show skeleton or simple loading text.
  - Prediction loading: disable upload button and show "识别中".
- Empty state:
  - If no models are enabled, show "暂无可用模型".
  - If no history exists, show "暂无识别记录".
- Error state:
  - Network error: show "网络异常，请稍后重试".
  - Login required: show login prompt.
  - File too large: show "图片不能超过 5MB".
  - Unsupported image type: show "仅支持 JPG、PNG、WEBP 图片".
  - Server unavailable outside service hours: show "服务暂不可用，请在开放时间内重试".
- Success feedback:
  - Prediction page updates inline with the result.
  - History page refreshes when returning from a successful prediction.

Form and upload validation:

1. Only allow images.
2. Prefer `wx.chooseMedia` for album/camera selection.
3. Use `wx.uploadFile`, with form field name `file`.
4. Include authenticated session token in request headers after login.

## 7. Backend Requirements

Recommended backend stack: FastAPI.

Recommended endpoint set:

1. `GET /api/health`
   - Purpose: health check for server and deployment.
   - Auth requirement: public.
   - Response:
     - `status`: string, `ok`
     - `service`: string, `ModelScope MiniLab API`
     - `time`: ISO datetime

2. `POST /api/auth/wechat-login`
   - Purpose: exchange WeChat `code` for application session.
   - Auth requirement: public.
   - Request JSON:
     - `code`: string, required.
   - Response:
     - `token`: string, application JWT or opaque session token.
     - `user`: object containing `id`, `openid_masked`, `nickname` if available.
   - Security:
     - Do not return raw `session_key`.
     - Store WeChat secrets in environment variables.

3. `GET /api/models`
   - Purpose: return enabled model list for the mini-program home page.
   - Auth requirement: public.
   - Response data per model:
     - `model_id`: string
     - `name`: string
     - `name_en`: string
     - `description`: string
     - `task_type`: string, e.g. `image_classification`
     - `input_type`: string, e.g. `image`
     - `enabled`: boolean
     - `cover_url`: string or null

4. `GET /api/models/{model_id}`
   - Purpose: return public model detail metadata.
   - Auth requirement: public.
   - Response:
     - same public metadata as model list
     - `supported_file_types`: array
     - `max_upload_mb`: number

5. `POST /api/models/{model_id}/predict`
   - Purpose: upload input and run inference for a selected model.
   - Auth requirement: login required.
   - Request:
     - multipart form field `file`: image file, required for cat-dog.
   - Path params:
     - `model_id`: string.
   - Response:
     - `request_id`: string
     - `model_id`: string
     - `label`: string, e.g. `cat` or `dog`
     - `label_cn`: string, e.g. `猫` or `狗`
     - `confidence`: number
     - `probabilities`: object, e.g. `{ "cat": 0.123, "dog": 0.877 }`
     - `latency_ms`: number
     - `created_at`: ISO datetime

6. `GET /api/predictions/history`
   - Purpose: return current user's prediction history.
   - Auth requirement: login required.
   - Query params:
     - `page`: integer, default 1.
     - `page_size`: integer, default 20, max 50.
   - Response:
     - `items`: array of prediction records.
     - `page`: integer.
     - `page_size`: integer.
     - `total`: integer.

Backend service logic:

1. Load model registry at startup.
2. Load the cat-dog PyTorch models once at startup or lazily on first request.
3. For cat-dog, preprocess images exactly as the training/evaluation pipeline requires:
   - RGB conversion.
   - Resize to 256 x 256.
   - Tensor conversion.
   - Normalize with ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.
4. Run PyTorch inference under `torch.inference_mode()`.
5. Compute cat-dog ensemble probability using weights 5:1:3.
6. Use threshold `prob_dog >= 0.5` for dog, otherwise cat.
7. Save prediction history metadata after successful inference.
8. Do not save original image bytes by default.
9. Return stable JSON errors without Python tracebacks.

## 8. Database Requirements

Use MySQL 8.x unless the implementation environment already provides another relational database and the user approves switching.

New tables:

### Table: `users`

- `id`: BIGINT primary key, auto increment.
- `openid`: VARCHAR(128), not null, unique.
- `unionid`: VARCHAR(128), nullable.
- `nickname`: VARCHAR(100), nullable.
- `avatar_url`: VARCHAR(500), nullable.
- `created_at`: DATETIME, not null.
- `updated_at`: DATETIME, not null.
- `last_login_at`: DATETIME, nullable.
- `deleted`: TINYINT(1), not null, default 0.

Indexes:

- Unique index `uk_users_openid` on `openid`.

### Table: `ai_models`

- `id`: BIGINT primary key, auto increment.
- `model_id`: VARCHAR(64), not null, unique.
- `name`: VARCHAR(100), not null.
- `name_en`: VARCHAR(100), nullable.
- `description`: VARCHAR(500), nullable.
- `task_type`: VARCHAR(64), not null.
- `input_type`: VARCHAR(64), not null.
- `output_type`: VARCHAR(64), not null.
- `enabled`: TINYINT(1), not null, default 1.
- `sort_order`: INT, not null, default 100.
- `cover_url`: VARCHAR(500), nullable.
- `created_at`: DATETIME, not null.
- `updated_at`: DATETIME, not null.
- `deleted`: TINYINT(1), not null, default 0.

Indexes:

- Unique index `uk_ai_models_model_id` on `model_id`.
- Normal index `idx_ai_models_enabled_sort` on `enabled`, `sort_order`.

Seed data:

- Insert one enabled model:
  - `model_id`: `cat-dog`
  - `name`: `猫狗图像二分类`
  - `name_en`: `Cat-Dog Classifier`
  - `task_type`: `image_classification`
  - `input_type`: `image`
  - `output_type`: `classification`
  - `enabled`: `1`
  - `sort_order`: `10`

### Table: `prediction_records`

- `id`: BIGINT primary key, auto increment.
- `request_id`: VARCHAR(64), not null, unique.
- `user_id`: BIGINT, not null.
- `model_id`: VARCHAR(64), not null.
- `input_type`: VARCHAR(64), not null.
- `original_filename`: VARCHAR(255), nullable.
- `file_size`: INT, nullable.
- `content_type`: VARCHAR(100), nullable.
- `result_label`: VARCHAR(100), not null.
- `result_label_cn`: VARCHAR(100), not null.
- `confidence`: DECIMAL(8,6), nullable.
- `probabilities_json`: JSON, nullable.
- `latency_ms`: INT, nullable.
- `status`: VARCHAR(32), not null.
- `error_code`: VARCHAR(64), nullable.
- `error_message`: VARCHAR(255), nullable.
- `created_at`: DATETIME, not null.
- `deleted`: TINYINT(1), not null, default 0.

Indexes:

- Unique index `uk_prediction_records_request_id` on `request_id`.
- Normal index `idx_prediction_records_user_created` on `user_id`, `created_at`.
- Normal index `idx_prediction_records_model_created` on `model_id`, `created_at`.

Data integrity:

1. `prediction_records.user_id` should reference `users.id` if migrations and ORM support foreign keys cleanly.
2. `prediction_records.model_id` should match a registered model ID.
3. Do not store original image bytes in this table.

## 9. State Machine

This feature has a lightweight lifecycle for prediction records.

States:

1. `success`: prediction completed and result was returned.
2. `failed`: prediction failed after request validation or inference started.

Initial state:

- There is no durable `pending` state in v1 because requests are synchronous. A database record is written after completion or failure.

Terminal states:

- `success`
- `failed`

Allowed transitions:

- In-memory request processing -> `success`
- In-memory request processing -> `failed`

Illegal transitions:

- `success` -> `failed` is forbidden.
- `failed` -> `success` is forbidden.
- Any terminal record must not be mutated to another status except for soft deletion if a future privacy feature requires it.

Trigger for each transition:

- `success`: backend validates request, model inference completes, and response data is available.
- `failed`: backend detects a validation, decoding, model, or server error after enough context exists to write a failure record.

Side effects bound to transition:

- `success`: insert one `prediction_records` row with result metadata in the same database transaction.
- `failed`: insert one `prediction_records` row with error metadata if a user and model ID are known.

## 10. Error Handling Requirements

Backend error responses must use a stable JSON shape:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "用户可理解的错误信息",
    "request_id": "..."
  }
}
```

Required cases:

1. Model not found:
   - HTTP 404.
   - Code: `MODEL_NOT_FOUND`.
   - Message: `模型不存在或暂不可用`.
2. Login required:
   - HTTP 401.
   - Code: `UNAUTHORIZED`.
   - Message: `请先登录`.
3. Invalid or expired token:
   - HTTP 401.
   - Code: `INVALID_TOKEN`.
   - Message: `登录状态已失效，请重新登录`.
4. File missing:
   - HTTP 400.
   - Code: `FILE_REQUIRED`.
   - Message: `请上传图片`.
5. File too large:
   - HTTP 400.
   - Code: `FILE_TOO_LARGE`.
   - Message: `图片不能超过 5MB`.
6. Unsupported file type:
   - HTTP 400.
   - Code: `UNSUPPORTED_FILE_TYPE`.
   - Message: `仅支持 JPG、PNG、WEBP 图片`.
7. Image decode failure:
   - HTTP 400.
   - Code: `INVALID_IMAGE`.
   - Message: `图片解析失败，请更换图片`.
8. Rate limited:
   - HTTP 429.
   - Code: `RATE_LIMITED`.
   - Message: `请求过于频繁，请稍后重试`.
9. Model inference failure:
   - HTTP 500.
   - Code: `INFERENCE_FAILED`.
   - Message: `模型识别失败，请稍后重试`.
10. Server unavailable outside planned service window:
   - HTTP 503 if service-window enforcement is implemented.
   - Code: `SERVICE_UNAVAILABLE`.
   - Message: `服务暂不可用，请在开放时间内重试`.

Frontend display behavior:

1. Show concise Chinese messages from the backend when safe.
2. Never display raw stack traces, exception class names, SQL errors, or Python errors.
3. If upload fails because the backend is unavailable, show a retry affordance.

## 11. Concurrency & Consistency

Transaction boundaries:

1. WeChat login:
   - Exchange code with WeChat API.
   - Upsert `users` by `openid`.
   - Update `last_login_at`.
   - Return application token.
   - User upsert and login timestamp update must be atomic.
2. Successful prediction:
   - Generate `request_id`.
   - Run inference.
   - Insert one `prediction_records` row with `status = success`.
   - The insert should be atomic.
3. Failed prediction record:
   - If user and model context are known, insert one `prediction_records` row with `status = failed`.
   - The insert should be atomic.

Idempotency keys:

1. Prediction:
   - Generate server-side `request_id` for each upload request.
   - v1 does not need client-supplied idempotency for predictions because duplicate uploads are acceptable as separate user actions.
   - Do not retry a timed-out upload automatically in the frontend without user action.
2. WeChat login:
   - `openid` is the natural idempotency key for user creation.
   - Unique index `uk_users_openid` prevents duplicate users.

Locking and anti-abuse strategy:

1. Use Redis-based rate limiting by user ID after login.
2. Also limit by IP or client fingerprint for unauthenticated public endpoints.
3. Suggested prediction limit:
   - Per user: 20 predictions per minute.
   - Per IP: 60 prediction requests per minute.
   - These values can be adjusted in environment configuration.
4. Use database unique constraints for `users.openid` and `prediction_records.request_id`.

Race conditions to defend against:

1. Two login requests for the same WeChat user arriving at the same time must not create duplicate users.
2. Multiple concurrent predictions from one user must be rate-limited and must each write at most one prediction record.
3. Backend startup must not load the same large model repeatedly per request.
4. If model loading fails, API should return a controlled error rather than accepting uploads that hang.

## 12. Permissions & Security

Login requirements:

1. `GET /api/health`: public.
2. `GET /api/models`: public.
3. `GET /api/models/{model_id}`: public.
4. `POST /api/auth/wechat-login`: public.
5. `POST /api/models/{model_id}/predict`: login required.
6. `GET /api/predictions/history`: login required.

Allowed roles:

- v1 has only normal users.
- Admin role is out of scope.

Authorization:

1. A user can only read their own prediction history.
2. Backend must derive user ID from the authenticated token, never from client-submitted user ID.

Secrets:

1. WeChat AppID, AppSecret, JWT secret, database URL, Redis URL, and any deployment secrets must be environment variables.
2. Do not hard-code secrets in source files.
3. Do not commit `.env` files.

File upload security:

1. Maximum upload size: 5 MB.
2. Validate MIME/content type and extension.
3. Decode with PIL and convert to RGB before inference.
4. Reject invalid images.
5. Do not store original image files by default.
6. Do not pass user filename directly into filesystem paths.

API security:

1. Enforce HTTPS in production.
2. Configure WeChat mini-program legal request/upload domains.
3. Restrict CORS to expected domains if a web frontend is ever added.
4. Apply rate limiting to prediction endpoints.
5. Log request ID, model ID, latency, and status; do not log tokens or raw image bytes.

Privacy:

1. Prediction history should store metadata and result only.
2. `openid` should not be returned raw to the frontend; return a masked value if needed.
3. Provide a future path for deleting history, but deletion UI can be deferred.

## 13. Engineering Constraints

1. Preserve the original cat-dog training project; treat it as a source of model assets, not as the production backend.
2. Read relevant code before modifying or copying model definitions.
3. Keep the implementation modular:
   - model registry owns metadata and routing;
   - predictor modules own preprocessing and inference;
   - API routes own HTTP request/response concerns.
4. Do not hard-code cat-dog behavior into generic model APIs.
5. Use CPU-compatible inference by default.
6. Do not require NVIDIA GPU or CUDA for production startup.
7. Avoid unnecessary dependencies.
8. If adding a dependency, document why it is needed.
9. Do not expose detailed model internals to normal users in v1.
10. Do not introduce payment, admin console, object storage, or image persistence unless explicitly requested later.
11. Use UTF-8 for all source and Markdown files.
12. Follow Windows path safety when working in the current environment.
13. Do not delete generated data, model checkpoints, or datasets.

## 14. Execution Flow

1. Read this Goal fully.
2. Inspect the existing cat-dog project:
   - `README.md`
   - `model.py`
   - `evaluate.py`
   - `requirements.txt`
   - checkpoint paths under `models/from_scratch/`
3. Create or inspect the `ModelScope MiniLab` project structure.
4. Produce a brief implementation plan before editing.
5. Implement backend foundation:
   - FastAPI app.
   - settings from environment variables.
   - health endpoint.
   - database connection.
   - Redis rate limiter.
   - stable error response shape.
6. Implement database migrations or schema initialization.
7. Implement model registry and seed metadata.
8. Implement WeChat login API.
9. Implement cat-dog predictor:
   - copy or import the required model definition safely;
   - load checkpoints once;
   - implement weighted ensemble inference;
   - return structured result.
10. Implement prediction API and history API.
11. Implement WeChat native mini-program pages:
   - home model cards;
   - model detail;
   - upload/predict flow;
   - history;
   - about.
12. Connect mini-program configuration to backend base URL.
13. Add tests and manual verification assets.
14. Run backend tests.
15. Run mini-program build/compile checks if available.
16. Document local startup and cloud deployment.
17. Output final summary with modified files, endpoints, tests, and remaining risks.

## 15. Acceptance Criteria

Must satisfy all of the following:

1. Project uses the names `ModelScope MiniLab` and `智模工坊`.
2. WeChat native mini-program has a home page showing model cards from backend data.
3. Cat-dog model appears as the first enabled model card.
4. Model detail page allows a logged-in user to choose or capture an image.
5. If the user is not logged in, prediction flow prompts WeChat login.
6. Backend implements `POST /api/auth/wechat-login`.
7. Backend implements `GET /api/models`.
8. Backend implements `GET /api/models/{model_id}`.
9. Backend implements `POST /api/models/{model_id}/predict`.
10. Backend implements `GET /api/predictions/history`.
11. Cat-dog prediction uses the EfficientNet-B0 v2/v3/v4 weighted ensemble with weights 5:1:3 by default.
12. Cat-dog preprocessing matches the original evaluation pipeline: RGB, 256 x 256 resize, tensor conversion, ImageNet normalization.
13. Prediction endpoint rejects files larger than 5 MB.
14. Prediction endpoint rejects unsupported file types.
15. Prediction endpoint returns `label_cn`.
16. Mini-program prediction result UI displays only `猫` or `狗` as the primary result in v1.
17. Backend response includes diagnostic fields: `request_id`, `model_id`, `label`, `label_cn`, `confidence`, `probabilities`, `latency_ms`, and `created_at`.
18. Successful predictions are saved to the current user's history.
19. History API returns only the authenticated user's records.
20. Original uploaded images are not persisted by default.
21. Redis or equivalent rate limiting protects prediction endpoints.
22. Error responses use the stable JSON error shape.
23. Production configuration uses environment variables for secrets.
24. Backend can run on CPU-only server.
25. The platform is extensible: adding a new image classification model should require a new predictor module and metadata entry, not rewrites to generic APIs.
26. Backend starts successfully.
27. Mini-program can complete the cat-dog prediction flow end-to-end against the backend.
28. API tests or documented manual tests cover login, model list, prediction success, invalid file, oversized file, rate limit, and history.
29. No original cat-dog training checkpoints or datasets are deleted or overwritten.
30. Final documentation explains local startup, production deployment, service hours, and WeChat domain configuration.

## 16. Testing Requirements

Backend automated tests where feasible:

1. `GET /api/health` returns status ok.
2. `GET /api/models` returns cat-dog model metadata.
3. `GET /api/models/cat-dog` returns supported file types and 5 MB limit.
4. `POST /api/models/cat-dog/predict` rejects unauthenticated requests.
5. Prediction endpoint rejects missing file.
6. Prediction endpoint rejects unsupported content type.
7. Prediction endpoint rejects file larger than 5 MB.
8. Prediction endpoint returns stable JSON for invalid image bytes.
9. Prediction endpoint returns `label_cn` and diagnostic fields for a valid test image.
10. History endpoint returns only current user's records.
11. WeChat login upsert does not create duplicate users for the same openid.
12. Rate limiter returns HTTP 429 when the configured limit is exceeded.

Manual verification:

1. Start backend locally with documented environment variables.
2. Open API docs if enabled by FastAPI.
3. Use Apifox/Postman/curl to call:
   - `GET /api/health`
   - `GET /api/models`
   - `GET /api/models/cat-dog`
   - `POST /api/models/cat-dog/predict`
   - `GET /api/predictions/history`
4. In WeChat Developer Tools:
   - open the mini-program;
   - verify model card list;
   - login with WeChat development credentials or mocked login in local mode;
   - select cat-dog model;
   - upload a cat image and verify primary result shows `猫`;
   - upload a dog image and verify primary result shows `狗`;
   - open history page and verify records appear.
5. Test network failure behavior by stopping backend and attempting prediction.
6. Test service-window messaging if the implementation enforces 10:00-18:00 availability.

WeChat login testing:

1. In local development, allow a mocked WeChat login provider only if real WeChat credentials are unavailable.
2. Mock mode must be clearly controlled by an environment variable, for example `WECHAT_AUTH_MOCK=true`.
3. Production must use real WeChat `code2Session` exchange.
4. Mock mode must never be enabled silently in production.

No external callbacks are required in v1.

## 17. Prohibited Actions

1. Do not start by coding before reading this Goal and inspecting relevant existing files.
2. Do not retrain the cat-dog model.
3. Do not delete or overwrite existing cat-dog checkpoints.
4. Do not store uploaded original images by default.
5. Do not hard-code WeChat AppSecret, JWT secret, database passwords, or Redis credentials.
6. Do not return raw `openid`, `session_key`, stack traces, or internal errors to the mini-program.
7. Do not expose model training details to normal users unless later requested.
8. Do not implement payment or membership features in v1.
9. Do not build an admin console in v1.
10. Do not make cat-dog-specific assumptions inside generic model list/detail APIs.
11. Do not bypass authentication for prediction history.
12. Do not fabricate test results.
13. Do not claim completion without running available verification steps.
14. Do not perform destructive filesystem operations.

## 18. Final Output

After implementation, output:

1. List of modified and created files, with a short explanation for each.
2. Final project directory structure.
3. New API endpoints and their purpose.
4. Database tables, columns, and indexes created.
5. How to configure environment variables.
6. How to start backend locally.
7. How to run the mini-program locally in WeChat Developer Tools.
8. How to deploy backend to a cloud server.
9. How to configure WeChat legal request/upload domains.
10. Test commands and manual verification steps performed.
11. Which acceptance criteria passed.
12. Known limitations:
    - CPU inference latency.
    - Service only intended for 10:00-18:00 unless server schedule changes.
    - Uploaded images not persisted in v1.
    - No admin console in v1.
13. Recommended future iterations after this Goal is implemented:
    - Admin model management.
    - Optional image history storage with user consent.
    - More model modules.
    - ONNX/TorchScript export for faster CPU inference.
    - Background task queue if inference load grows.
