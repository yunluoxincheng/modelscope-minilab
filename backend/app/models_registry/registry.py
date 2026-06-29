"""In-memory registry that maps model_id to ModelMeta and resolves a predictor."""
from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional

from .base import ModelMeta
from .entries import default_models


class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, ModelMeta] = {}
        self._lock = Lock()

    def register(self, meta: ModelMeta) -> None:
        with self._lock:
            self._models[meta.model_id] = meta

    def get(self, model_id: str) -> Optional[ModelMeta]:
        return self._models.get(model_id)

    def require(self, model_id: str) -> ModelMeta:
        from ..core.errors import ModelNotFoundError
        meta = self.get(model_id)
        if meta is None or not meta.enabled:
            raise ModelNotFoundError()
        return meta

    def list_all(self) -> List[ModelMeta]:
        return sorted(
            self._models.values(),
            key=lambda m: (m.sort_order, m.model_id),
        )

    def list_enabled(self) -> List[ModelMeta]:
        return [m for m in self.list_all() if m.enabled]


_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
        for meta in default_models():
            _registry.register(meta)
    return _registry


def list_public_models() -> List[ModelMeta]:
    return get_registry().list_enabled()
