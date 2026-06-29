"""Stable error response shape and unified exception handling."""
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    """Application-level error that maps to the stable JSON error shape."""

    status_code: int = 400
    code: str = "ERROR_CODE"
    message: str = "请求出错"

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.request_id = request_id
        self.extra = extra or {}
        super().__init__(self.message)


class ModelNotFoundError(ApiError):
    status_code = 404
    code = "MODEL_NOT_FOUND"
    message = "模型不存在或暂不可用"


class UnauthorizedError(ApiError):
    status_code = 401
    code = "UNAUTHORIZED"
    message = "请先登录"


class InvalidTokenError(ApiError):
    status_code = 401
    code = "INVALID_TOKEN"
    message = "登录状态已失效，请重新登录"


class FileRequiredError(ApiError):
    status_code = 400
    code = "FILE_REQUIRED"
    message = "请上传图片"


class FileTooLargeError(ApiError):
    status_code = 400
    code = "FILE_TOO_LARGE"
    message = "图片不能超过 5MB"


class UnsupportedFileTypeError(ApiError):
    status_code = 400
    code = "UNSUPPORTED_FILE_TYPE"
    message = "仅支持 JPG、PNG、WEBP 图片"


class InvalidImageError(ApiError):
    status_code = 400
    code = "INVALID_IMAGE"
    message = "图片解析失败，请更换图片"


class RateLimitedError(ApiError):
    status_code = 429
    code = "RATE_LIMITED"
    message = "请求过于频繁，请稍后重试"


class InferenceFailedError(ApiError):
    status_code = 500
    code = "INFERENCE_FAILED"
    message = "模型识别失败，请稍后重试"


class ServiceUnavailableError(ApiError):
    status_code = 503
    code = "SERVICE_UNAVAILABLE"
    message = "服务暂不可用，请在开放时间内重试"


def new_request_id() -> str:
    return uuid.uuid4().hex


def error_payload(
    code: str,
    message: str,
    request_id: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "error": {"code": code, "message": message, "request_id": request_id}
    }
    if extra:
        payload["error"].update(extra)
    return payload


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _handle_api_error(_: Request, exc: ApiError):
        rid = exc.request_id or new_request_id()
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.code, exc.message, rid, exc.extra),
            headers={"X-Request-Id": rid},
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http(_: Request, exc: StarletteHTTPException):
        rid = new_request_id()
        message_map = {
            401: "请先登录",
            403: "无权访问",
            404: "资源不存在",
            422: "请求参数有误",
            500: "服务器内部错误",
        }
        message = message_map.get(exc.status_code, "请求失败")
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload("HTTP_ERROR", message, rid),
            headers={"X-Request-Id": rid},
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(_: Request, exc: RequestValidationError):
        rid = new_request_id()
        return JSONResponse(
            status_code=422,
            content=error_payload("VALIDATION_ERROR", "请求参数有误", rid),
            headers={"X-Request-Id": rid},
        )

    @app.exception_handler(Exception)
    async def _handle_unhandled(_: Request, exc: Exception):
        rid = new_request_id()
        return JSONResponse(
            status_code=500,
            content=error_payload("INTERNAL_ERROR", "服务器内部错误，请稍后重试", rid),
            headers={"X-Request-Id": rid},
        )
