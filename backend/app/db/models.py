"""SQLAlchemy ORM models for the three core tables."""
from __future__ import annotations

import datetime as _dt
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    """Declarative base for all models."""


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("openid", name="uk_users_openid"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(128), nullable=False, unique=True)
    unionid = Column(String(128), nullable=True)
    nickname = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)
    last_login_at = Column(DateTime, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))


class AiModel(Base):
    __tablename__ = "ai_models"
    __table_args__ = (
        UniqueConstraint("model_id", name="uk_ai_models_model_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String(64), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    task_type = Column(String(64), nullable=False)
    input_type = Column(String(64), nullable=False)
    output_type = Column(String(64), nullable=False, default="classification")
    enabled = Column(Boolean, nullable=False, default=True, server_default=text("1"))
    sort_order = Column(Integer, nullable=False, default=100, server_default=text("100"))
    cover_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)
    deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))


class PredictionRecord(Base):
    __tablename__ = "prediction_records"
    __table_args__ = (
        UniqueConstraint("request_id", name="uk_prediction_records_request_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(64), nullable=False, unique=True)
    user_id = Column(Integer, nullable=False, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    input_type = Column(String(64), nullable=False)
    original_filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    result_label = Column(String(100), nullable=False)
    result_label_cn = Column(String(100), nullable=False)
    confidence = Column(Numeric(8, 6), nullable=True)
    probabilities_json = Column(JSON, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    status = Column(String(32), nullable=False)
    error_code = Column(String(64), nullable=True)
    error_message = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now, index=True)
    deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))


TERMINAL_STATUSES = {"success", "failed"}
