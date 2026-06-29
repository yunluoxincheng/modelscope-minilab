"""API integration tests covering acceptance criteria."""
from __future__ import annotations

import io

from PIL import Image


def _oversized_jpeg_bytes() -> bytes:
    """Create a JPEG definitely over 5MB by padding random noise into pixels."""
    import random

    img = Image.new("RGB", (2400, 2400))
    pixels = img.load()
    for y in range(0, 2400, 4):
        for x in range(0, 2400, 4):
            pixels[x, y] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=98)
    data = buf.getvalue()
    # Guarantee we exceed 5MB even on systems where compression is aggressive.
    target = 6 * 1024 * 1024
    if len(data) < target:
        data = data + (b"\xff\xff" * ((target - len(data)) // 2 + 1))
    return data[:target + 100]


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "ModelScope" in data["service"]


def test_models_list_contains_cat_dog(client):
    resp = client.get("/api/models")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(m["model_id"] == "cat-dog" for m in items)
    cat_dog = next(m for m in items if m["model_id"] == "cat-dog")
    assert cat_dog["name"] == "猫狗图像二分类"
    assert cat_dog["task_type"] == "image_classification"
    assert cat_dog["input_type"] == "image"


def test_model_detail(client):
    resp = client.get("/api/models/cat-dog")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_id"] == "cat-dog"
    assert "image/jpeg" in data["supported_file_types"]
    assert data["max_upload_mb"] == 5


def test_model_not_found(client):
    resp = client.get("/api/models/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "MODEL_NOT_FOUND"


def test_predict_requires_auth(client, sample_cat_image_bytes):
    resp = client.post(
        "/api/models/cat-dog/predict",
        files={"file": ("cat.jpg", sample_cat_image_bytes, "image/jpeg")},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_predict_missing_file(client, auth_headers):
    resp = client.post("/api/models/cat-dog/predict", headers=auth_headers)
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] in {"FILE_REQUIRED", "VALIDATION_ERROR"}


def test_predict_unsupported_type(client, auth_headers):
    resp = client.post(
        "/api/models/cat-dog/predict",
        headers=auth_headers,
        files={"file": ("file.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_predict_oversized_file(client, auth_headers):
    big = _oversized_jpeg_bytes()
    resp = client.post(
        "/api/models/cat-dog/predict",
        headers=auth_headers,
        files={"file": ("big.jpg", big, "image/jpeg")},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_predict_invalid_image(client, auth_headers, invalid_image_bytes):
    resp = client.post(
        "/api/models/cat-dog/predict",
        headers=auth_headers,
        files={"file": ("bad.jpg", invalid_image_bytes, "image/jpeg")},
    )
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "INFERENCE_FAILED"


def test_predict_success_returns_label_cn_and_diagnostics(
    client, auth_headers, sample_cat_image_bytes
):
    resp = client.post(
        "/api/models/cat-dog/predict",
        headers=auth_headers,
        files={"file": ("cat.jpg", sample_cat_image_bytes, "image/jpeg")},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["model_id"] == "cat-dog"
    assert data["label"] in {"cat", "dog"}
    assert data["label_cn"] in {"猫", "狗"}
    assert "cat" in data["probabilities"] and "dog" in data["probabilities"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["latency_ms"], int)
    assert data["request_id"]
    assert data["created_at"]


def test_history_returns_only_current_user(client, auth_headers, sample_cat_image_bytes):
    for _ in range(2):
        client.post(
            "/api/models/cat-dog/predict",
            headers=auth_headers,
            files={"file": ("c.jpg", sample_cat_image_bytes, "image/jpeg")},
        )
    resp = client.get("/api/predictions/history", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 2
    assert all(item["model_id"] == "cat-dog" for item in body["items"])


def test_history_requires_auth(client):
    resp = client.get("/api/predictions/history")
    assert resp.status_code == 401


def test_login_upsert_is_idempotent(client):
    r1 = client.post("/api/auth/wechat-login", json={"code": "stable-code"})
    r2 = client.post("/api/auth/wechat-login", json={"code": "stable-code"})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["user"]["id"] == r2.json()["user"]["id"]


def test_invalid_token_rejected(client):
    resp = client.get(
        "/api/predictions/history",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] in {"INVALID_TOKEN", "UNAUTHORIZED"}


def test_error_shape_is_stable(client):
    resp = client.get("/api/models/missing")
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    err = body["error"]
    for key in ("code", "message", "request_id"):
        assert key in err
