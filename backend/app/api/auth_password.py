"""Username + password auth endpoints for the web frontend.

微信登录的 code 只有小程序能换取，浏览器端无法使用，因此 web 端使用
独立的用户名密码体系：复用 users 表（username/password_hash 列）与
同一套 JWT 签发/校验，登录后的 token 与微信登录完全等价。
"""
from __future__ import annotations

import datetime as _dt
import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from ..core.errors import InvalidCredentialsError, ServiceUnavailableError, UsernameTakenError
from ..core.rate_limit import get_limiter
from ..core.security import create_token, hash_password, verify_password
from ..core.settings import Settings, get_settings
from ..db.models import User
from ..db.repositories import create_password_user, get_user_by_username
from ..db.session import get_db
from .deps import get_client_ip, get_request_id

router = APIRouter()
log = logging.getLogger(__name__)


class RegisterRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=32,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="3-32 位字母/数字/下划线/中划线",
    )
    password: str = Field(..., min_length=6, max_length=64)
    nickname: str | None = Field(default=None, max_length=32)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=1, max_length=64)


class TokenResponse(BaseModel):
    token: str
    user: dict


def _user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "openid_masked": None,
    }


def _issue_token(user: User, request_id: str, settings: Settings) -> TokenResponse:
    token = create_token({"uid": user.id, "rid": request_id}, settings)
    return TokenResponse(token=token, user=_user_payload(user))


@router.post("/auth/register", response_model=TokenResponse)
async def register(
    payload: RegisterRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
    db=Depends(get_db),
    client_ip: str = Depends(get_client_ip),
    request_id: str = Depends(get_request_id),
):
    get_limiter().require(
        f"rl:register:ip:{client_ip}",
        limit=settings.public_rate_per_ip_per_minute,
    )

    if get_user_by_username(db, payload.username) is not None:
        raise UsernameTakenError()

    try:
        user = create_password_user(
            db,
            username=payload.username,
            password_hash=hash_password(payload.password),
            nickname=payload.nickname,
        )
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        log.exception("register db write failed request_id=%s", request_id)
        raise ServiceUnavailableError("注册服务暂不可用，请稍后重试") from exc

    return _issue_token(user, request_id, settings)


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
    db=Depends(get_db),
    client_ip: str = Depends(get_client_ip),
    request_id: str = Depends(get_request_id),
):
    get_limiter().require(
        f"rl:login:ip:{client_ip}",
        limit=settings.public_rate_per_ip_per_minute,
    )

    user = get_user_by_username(db, payload.username)
    if user is None or user.password_hash is None:
        # 用户不存在与密码错误返回同一错误，避免用户名枚举。
        raise InvalidCredentialsError()
    if not verify_password(payload.password, user.password_hash):
        raise InvalidCredentialsError()

    try:
        user.last_login_at = _dt.datetime.utcnow()
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        log.exception("login db write failed request_id=%s", request_id)
        raise ServiceUnavailableError("登录服务暂不可用，请稍后重试") from exc

    return _issue_token(user, request_id, settings)
