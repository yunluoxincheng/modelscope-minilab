"""Repository helpers wrapping common DB queries."""
from __future__ import annotations

import datetime as _dt
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AiModel, PredictionRecord, User


def upsert_user_by_openid(
    sess: Session,
    openid: str,
    *,
    unionid: Optional[str] = None,
    nickname: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> User:
    user = sess.execute(select(User).where(User.openid == openid)).scalar_one_or_none()
    now = _dt.datetime.utcnow()
    if user is None:
        user = User(
            openid=openid,
            unionid=unionid,
            nickname=nickname,
            avatar_url=avatar_url,
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )
        sess.add(user)
        sess.flush()
    else:
        user.last_login_at = now
        user.updated_at = now
        if nickname:
            user.nickname = nickname
        if avatar_url:
            user.avatar_url = avatar_url
        if unionid:
            user.unionid = unionid
        sess.flush()
    return user


def get_user(sess: Session, user_id: int) -> Optional[User]:
    return sess.execute(select(User).where(User.id == user_id)).scalar_one_or_none()


def insert_prediction(sess: Session, **fields) -> PredictionRecord:
    record = PredictionRecord(**fields)
    sess.add(record)
    sess.flush()
    return record


def list_user_predictions(
    sess: Session,
    user_id: int,
    *,
    page: int = 1,
    page_size: int = 20,
):
    page = max(1, page)
    page_size = max(1, min(50, page_size))
    offset = (page - 1) * page_size
    base = (
        select(PredictionRecord)
        .where(PredictionRecord.user_id == user_id)
        .where(PredictionRecord.deleted.is_(False))
    )
    total = sess.execute(
        select(PredictionRecord.id).where(PredictionRecord.user_id == user_id).where(PredictionRecord.deleted.is_(False))
    ).all()
    items = (
        sess.execute(
            base.order_by(PredictionRecord.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return items, len(total)


def upsert_ai_model(sess: Session, **fields) -> AiModel:
    model_id = fields["model_id"]
    existing = sess.execute(
        select(AiModel).where(AiModel.model_id == model_id)
    ).scalar_one_or_none()
    if existing is None:
        existing = AiModel(**fields)
        sess.add(existing)
    else:
        for k, v in fields.items():
            setattr(existing, k, v)
    sess.flush()
    return existing


def list_enabled_ai_models(sess: Session):
    return (
        sess.execute(
            select(AiModel)
            .where(AiModel.enabled.is_(True))
            .where(AiModel.deleted.is_(False))
            .order_by(AiModel.sort_order.asc(), AiModel.id.asc())
        )
        .scalars()
        .all()
    )


def get_ai_model(sess: Session, model_id: str) -> Optional[AiModel]:
    return sess.execute(
        select(AiModel).where(AiModel.model_id == model_id)
    ).scalar_one_or_none()
