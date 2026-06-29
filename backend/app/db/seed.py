"""Seed ai_models table from the in-memory registry on startup."""
from __future__ import annotations

import logging

from ..models_registry import get_registry
from .repositories import upsert_ai_model
from .session import session_scope

log = logging.getLogger(__name__)


def seed_models() -> int:
    """Insert or update each registered model row. Returns count touched."""
    registry = get_registry()
    count = 0
    with session_scope() as sess:
        for meta in registry.list_all():
            upsert_ai_model(
                sess,
                model_id=meta.model_id,
                name=meta.name,
                name_en=meta.name_en,
                description=meta.description,
                task_type=meta.task_type,
                input_type=meta.input_type,
                output_type=meta.output_type,
                enabled=meta.enabled,
                sort_order=meta.sort_order,
                cover_url=meta.cover_url,
            )
            count += 1
    log.info("seeded %d ai_models rows", count)
    return count
