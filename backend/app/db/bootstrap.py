"""Create database schema on startup for fresh environments."""
from __future__ import annotations

import logging

from .models import Base
from .session import get_engine

log = logging.getLogger(__name__)


def create_all() -> None:
    Base.metadata.create_all(get_engine())
    log.info("database schema ensured")
