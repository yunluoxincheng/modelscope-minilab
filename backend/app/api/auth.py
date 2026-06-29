"""WeChat login endpoint."""
from __future__ import annotations

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from ..core.errors import InvalidTokenError, ServiceUnavailableError
from ..core.rate_limit import get_limiter
from ..core.security import create_token, mask_openid
from ..core.settings import Settings, get_settings
from ..db.repositories import upsert_user_by_openid
from ..db.session import get_db
from .deps import get_client_ip, get_request_id

router = APIRouter()
log = logging.getLogger(__name__)


class WechatLoginRequest(BaseModel):
    code: str = Field(..., description="wx.login() returned code")
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class WechatLoginResponse(BaseModel):
    token: str
    user: dict


WECHAT_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def _exchange_code_real(code: str, settings: Settings) -> dict:
    params = {
        "appid": settings.wechat_app_id,
        "secret": settings.wechat_app_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(WECHAT_CODE2SESSION_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        log.warning("wechat code2Session failed: %s", exc)
        raise ServiceUnavailableError("微信登录暂不可用，请稍后重试") from exc

    openid = data.get("openid")
    if not openid:
        log.warning("wechat code2Session returned no openid: %s", data)
        raise InvalidTokenError("微信登录失败，请重试")
    return {
        "openid": openid,
        "unionid": data.get("unionid"),
        "session_key": data.get("session_key"),
    }


def _exchange_code_mock(code: str, settings: Settings) -> dict:
    # In mock mode we treat the code itself as a deterministic openid for local dev/tests.
    openid = f"mock-{code[:32]}" if code else "mock-anonymous"
    return {"openid": openid, "unionid": None, "session_key": "mock"}


@router.post("/auth/wechat-login", response_model=WechatLoginResponse)
async def wechat_login(
    payload: WechatLoginRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
    db=Depends(get_db),
    client_ip: str = Depends(get_client_ip),
    request_id: str = Depends(get_request_id),
):
    get_limiter().require(
        f"rl:wechat-login:ip:{client_ip}",
        limit=settings.public_rate_per_ip_per_minute,
    )

    if settings.wechat_auth_mock:
        if settings.env == "prod":
            log.error("FATAL: wechat_auth_mock must not be enabled in prod env")
            raise ServiceUnavailableError()
        wechat_data = _exchange_code_mock(payload.code, settings)
    else:
        if not settings.wechat_app_id or not settings.wechat_app_secret:
            raise ServiceUnavailableError("微信登录未配置，请联系管理员")
        wechat_data = await _exchange_code_real(payload.code, settings)

    user = upsert_user_by_openid(
        db,
        wechat_data["openid"],
        unionid=wechat_data.get("unionid"),
        nickname=payload.nickname,
        avatar_url=payload.avatar_url,
    )
    db.commit()

    token = create_token({"uid": user.id, "rid": request_id}, settings)
    return WechatLoginResponse(
        token=token,
        user={
            "id": user.id,
            "openid_masked": mask_openid(user.openid),
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
        },
    )
