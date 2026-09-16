"""Web 端用户名+密码认证（/api/auth/register、/api/auth/login）集成测试。"""
from __future__ import annotations

import uuid


def _unique_username(prefix: str = "user") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_register_success_returns_token_and_user(client):
    username = _unique_username()
    resp = client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret123", "nickname": "小明"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["token"]
    assert data["user"]["username"] == username
    assert data["user"]["nickname"] == "小明"
    assert data["user"]["id"] > 0


def test_register_token_can_call_authorized_api(client):
    username = _unique_username()
    reg = client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret123"},
    )
    token = reg.json()["token"]
    resp = client.get(
        "/api/predictions/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_register_duplicate_username_conflict(client):
    username = _unique_username()
    body = {"username": username, "password": "secret123"}
    r1 = client.post("/api/auth/register", json=body)
    r2 = client.post("/api/auth/register", json=body)
    assert r1.status_code == 200
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "USERNAME_TAKEN"


def test_register_rejects_bad_username(client):
    for bad in ("ab", "有中文", "space in", "x" * 33, ""):
        resp = client.post(
            "/api/auth/register",
            json={"username": bad, "password": "secret123"},
        )
        assert resp.status_code == 422, f"username={bad!r} should be invalid"


def test_register_rejects_short_password(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": _unique_username(), "password": "12345"},
    )
    assert resp.status_code == 422


def test_login_success_returns_same_user(client):
    username = _unique_username()
    reg = client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret123", "nickname": "甲"},
    )
    login = client.post(
        "/api/auth/login", json={"username": username, "password": "secret123"}
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["id"] == reg.json()["user"]["id"]
    assert login.json()["token"]


def test_login_wrong_password(client):
    username = _unique_username()
    client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret123"},
    )
    resp = client.post(
        "/api/auth/login", json={"username": username, "password": "wrong-pass"}
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_user_same_error_as_wrong_password(client):
    resp = client.post(
        "/api/auth/login",
        json={"username": "no_such_user_xyz", "password": "whatever1"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_wechat_user_cannot_password_login(client):
    # 微信登录建的用户没有 username/password_hash，不能走密码登录。
    client.post("/api/auth/wechat-login", json={"code": "wechat-only-code"})
    resp = client.post(
        "/api/auth/login",
        json={"username": "mock-wechat-only-code"[:24], "password": "whatever1"},
    )
    assert resp.status_code == 401


def test_predict_with_web_token(client, sample_cat_image_bytes):
    username = _unique_username()
    reg = client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret123"},
    )
    token = reg.json()["token"]
    resp = client.post(
        "/api/models/cat-dog/predict",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("cat.jpg", sample_cat_image_bytes, "image/jpeg")},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["label"] in {"cat", "dog"}

    history = client.get(
        "/api/predictions/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert history.status_code == 200
    assert history.json()["total"] == 1
