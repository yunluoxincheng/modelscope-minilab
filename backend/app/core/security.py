"""JWT issuance, password hashing and token extraction utilities."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from fastapi import Header, Request

from .errors import InvalidTokenError
from .settings import Settings, get_settings

# PBKDF2-SHA256 参数：iterations 对个人作品集的登录频率足够安全，
# 用标准库实现避免 bcrypt/cryptography 在多架构镜像里的编译负担。
_PBKDF2_ITERATIONS = 200_000
_SALT_BYTES = 16


def create_token(payload: Dict[str, Any], settings: Optional[Settings] = None) -> str:
    settings = settings or get_settings()
    now = datetime.now(timezone.utc)
    body = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.jwt_expire_hours)).timestamp()),
    }
    return jwt.encode(body, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, settings: Optional[Settings] = None) -> Dict[str, Any]:
    settings = settings or get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise InvalidTokenError("登录已过期") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError() from exc


def mask_openid(openid: str) -> str:
    if not openid:
        return ""
    if len(openid) <= 6:
        return openid[:1] + "***"
    return openid[:3] + "***" + openid[-3:]


def hash_password(password: str) -> str:
    salt = secrets.token_hex(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("ascii"), _PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: Optional[str]) -> bool:
    if not stored:
        return False
    parts = stored.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    try:
        iterations = int(parts[1])
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), parts[2].encode("ascii"), iterations
    ).hex()
    return hmac.compare_digest(digest, parts[3])


def extract_token(request: Request, authorization: Optional[str]) -> Optional[str]:
    header = authorization
    if header is None:
        header = request.headers.get("authorization")
    if not header:
        return None
    parts = header.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return header.strip()


def require_token(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """FastAPI dependency: require a valid bearer token."""
    from fastapi import Request as _R  # local import to keep signature simple
    if not authorization:
        raise InvalidTokenError()
    return decode_token(authorization)
