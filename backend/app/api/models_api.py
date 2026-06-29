"""Model list and detail endpoints (public)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.settings import Settings, get_settings
from ..models_registry import get_registry

router = APIRouter()


@router.get("/models")
def list_models(settings: Settings = Depends(get_settings)):
    registry = get_registry()
    return {
        "items": [m.to_public_dict() for m in registry.list_enabled()],
        "total": len(registry.list_enabled()),
    }


@router.get("/models/{model_id}")
def get_model(model_id: str, settings: Settings = Depends(get_settings)):
    meta = get_registry().require(model_id)
    return meta.to_detail_dict(settings)
