"""Pytest fixtures: isolated sqlite DB, mocked WeChat login, real model checkpoints."""
from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="session")
def settings_env(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("db") / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file.as_posix()}"
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"
    os.environ["WECHAT_AUTH_MOCK"] = "true"
    os.environ["JWT_SECRET"] = "test-secret-not-for-prod-please-rotate-in-real-deployments-32+"
    os.environ["SERVICE_WINDOW_ENFORCE"] = "false"
    os.environ["MAX_UPLOAD_MB"] = "5"
    os.environ["PREDICT_RATE_PER_USER_PER_MINUTE"] = "1000"
    os.environ["PREDICT_RATE_PER_IP_PER_MINUTE"] = "1000"
    os.environ["PUBLIC_RATE_PER_IP_PER_MINUTE"] = "1000"
    os.environ["CAT_DOG_ENABLE"] = "true"

    # Lazy import so env vars take effect.
    from app.core.settings import get_settings
    get_settings.cache_clear()

    # Rebuild engine bound to the test DB.
    from app.db import session as db_session
    db_session.reset_engine_for_tests()

    # Reset singletons.
    from app.core import rate_limit as rl
    rl.reset_limiter_for_tests()
    from app.predictors import factory
    factory.reset_for_tests()

    yield


@pytest.fixture()
def client(settings_env) -> Iterator[TestClient]:
    from app.main import create_app
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_token(client: TestClient) -> str:
    resp = client.post("/api/auth/wechat-login", json={"code": "test-code-001"})
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


@pytest.fixture()
def auth_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def sample_cat_image_bytes() -> bytes:
    """Generate a small JPEG in-memory so tests don't depend on real files."""
    from PIL import Image

    img = Image.new("RGB", (256, 256), color=(180, 120, 80))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture()
def sample_png_bytes() -> bytes:
    from PIL import Image

    img = Image.new("RGB", (128, 128), color=(50, 100, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture()
def invalid_image_bytes() -> bytes:
    return b"not-an-image-just-bytes"
