"""Create database schema on startup, and patch existing tables with new columns.

Base.metadata.create_all 只建缺失的表，不会给已存在的表加列；生产 SQLite
库落在卷里长期复用，因此启动时按模型定义做一次轻量补列（幂等）。
"""
from __future__ import annotations

import logging

from sqlalchemy import inspect, text

from .models import Base
from .session import get_engine

log = logging.getLogger(__name__)

# 已上线库需要补的列：表名 -> [(列名, DDL 类型)]
_PENDING_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "users": [
        ("username", "VARCHAR(64)"),
        ("password_hash", "VARCHAR(255)"),
    ],
}


def _add_missing_columns() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    for table, columns in _PENDING_COLUMNS.items():
        if not inspector.has_table(table):
            continue
        existing = {c["name"] for c in inspector.get_columns(table)}
        with engine.begin() as conn:
            for name, ddl in columns:
                if name in existing:
                    continue
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
                log.info("migrated: added column %s.%s", table, name)


def create_all() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    _add_missing_columns()
    log.info("database schema ensured")
