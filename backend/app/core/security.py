"""JWT issuance and verification utilities."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from fastapi import Header, Request

from .errors import InvalidTokenError
from .settings import Settings, get_settings


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
