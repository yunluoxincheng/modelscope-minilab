"""Shared FastAPI dependencies: DB session, current user, request-id, client IP."""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from ..core.errors import InvalidTokenError, UnauthorizedError
from ..core.security import decode_token, extract_token
from ..core.settings import Settings, get_settings
from ..db.models import User
from ..db.repositories import get_user
from ..db.session import get_db


def get_request_id(x_request_id: Optional[str] = Header(default=None)) -> str:
    from ..core.errors import new_request_id

    return x_request_id or new_request_id()


def get_settings_dep() -> Settings:
    return get_settings()


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    authorization: Optional[str] = Header(default=None),
) -> User:
    token = extract_token(request, authorization)
    if not token:
        raise UnauthorizedError()
    payload = decode_token(token, settings)
    user_id = payload.get("uid")
    if user_id is None:
        raise InvalidTokenError()
    user = get_user(db, int(user_id))
    if user is None:
        raise InvalidTokenError()
    return user


def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    authorization: Optional[str] = Header(default=None),
) -> Optional[User]:
    try:
        token = extract_token(request, authorization)
        if not token:
            return None
        payload = decode_token(token, settings)
    except Exception:
        return None
    user_id = payload.get("uid")
    if user_id is None:
        return None
    return get_user(db, int(user_id))
