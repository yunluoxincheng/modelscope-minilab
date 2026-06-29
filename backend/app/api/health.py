"""Health check endpoint."""
from __future__ import annotations

import datetime as _dt

from fastapi import APIRouter, Depends

from .. import __service_name__
from ..core.settings import Settings, get_settings

router = APIRouter()


@router.get("/health")
def health(settings: Settings = Depends(get_settings)):
    return {
        "status": "ok",
        "service": __service_name__,
        "time": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "env": settings.env,
    }
