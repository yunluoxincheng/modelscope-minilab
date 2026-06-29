"""Prediction upload endpoint and history endpoint."""
from __future__ import annotations

import datetime as _dt
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from sqlalchemy.orm import Session

from ..core.errors import (
    FileRequiredError,
    FileTooLargeError,
    InferenceFailedError,
    ServiceUnavailableError,
    UnsupportedFileTypeError,
)
from ..core.rate_limit import get_limiter
from ..core.settings import Settings, get_settings
from ..db.models import PredictionRecord, User
from ..db.repositories import insert_prediction, list_user_predictions
from ..db.session import get_db
from ..models_registry import get_registry
from ..predictors.factory import get_predictor
from .deps import get_client_ip, get_current_user, get_request_id

router = APIRouter()
log = logging.getLogger(__name__)


def _validate_upload(content_type: Optional[str], file_size: int, settings: Settings) -> str:
    if not content_type:
        raise UnsupportedFileTypeError()
    ct = content_type.lower().split(";", 1)[0].strip()
    if ct not in {t.lower() for t in settings.allowed_image_types}:
        raise UnsupportedFileTypeError()
    if file_size > settings.max_upload_mb * 1024 * 1024:
        raise FileTooLargeError()
    return ct


@router.post("/models/{model_id}/predict")
async def predict(
    model_id: str,
    request: Request,
    file: Optional[UploadFile] = File(default=None),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    client_ip: str = Depends(get_client_ip),
    request_id: str = Depends(get_request_id),
):
    if not settings.service_enabled:
        raise ServiceUnavailableError()

    meta = get_registry().require(model_id)

    get_limiter().require(
        f"rl:predict:user:{user.id}",
        limit=settings.predict_rate_per_user_per_minute,
    )
    get_limiter().require(
        f"rl:predict:ip:{client_ip}",
        limit=settings.predict_rate_per_ip_per_minute,
    )

    if file is None:
        raise FileRequiredError()

    raw = await file.read()
    if not raw:
        raise FileRequiredError()

    content_type = _validate_upload(file.content_type, len(raw), settings)

    predictor = get_predictor(model_id)
    try:
        result = predictor.predict(
            file_bytes=raw,
            content_type=content_type,
            filename=file.filename,
        )
    except Exception as exc:
        log.warning("predict failed model_id=%s request_id=%s err=%s", model_id, request_id, exc)
        _record_failure(db, user.id, model_id, content_type, file, len(raw), request_id, exc)
        raise InferenceFailedError() from exc

    created_at = _dt.datetime.utcnow()
    record = insert_prediction(
        db,
        request_id=request_id,
        user_id=user.id,
        model_id=model_id,
        input_type=meta.input_type,
        original_filename=file.filename,
        file_size=len(raw),
        content_type=content_type,
        result_label=result.label,
        result_label_cn=result.label_cn,
        confidence=result.confidence,
        probabilities_json=result.probabilities,
        latency_ms=result.extra.get("latency_ms"),
        status="success",
        created_at=created_at,
    )
    db.commit()

    return {
        "request_id": request_id,
        "model_id": model_id,
        "label": result.label,
        "label_cn": result.label_cn,
        "confidence": result.confidence,
        "probabilities": result.probabilities,
        "latency_ms": result.extra.get("latency_ms"),
        "created_at": created_at.isoformat() + "Z",
    }


def _record_failure(
    db: Session,
    user_id: int,
    model_id: str,
    content_type: str,
    file: Optional[UploadFile],
    file_size: int,
    request_id: str,
    exc: Exception,
) -> None:
    try:
        insert_prediction(
            db,
            request_id=f"{request_id}-fail",
            user_id=user_id,
            model_id=model_id,
            input_type="image",
            original_filename=getattr(file, "filename", None),
            file_size=file_size,
            content_type=content_type,
            result_label="unknown",
            result_label_cn="未知",
            status="failed",
            error_code="INFERENCE_FAILED",
            error_message=str(exc)[:240] if str(exc) else exc.__class__.__name__,
        )
        db.commit()
    except Exception:  # pragma: no cover - never mask original error
        db.rollback()


@router.get("/predictions/history")
def history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = list_user_predictions(db, user.id, page=page, page_size=page_size)
    return {
        "items": [_record_to_dict(r) for r in items],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def _record_to_dict(r: PredictionRecord) -> dict:
    return {
        "id": r.id,
        "request_id": r.request_id,
        "model_id": r.model_id,
        "result_label": r.result_label,
        "result_label_cn": r.result_label_cn,
        "confidence": float(r.confidence) if r.confidence is not None else None,
        "probabilities": r.probabilities_json,
        "latency_ms": r.latency_ms,
        "status": r.status,
        "created_at": r.created_at.isoformat() + "Z",
    }
