"""Redis-backed sliding rate limiter with an in-memory fallback."""
from __future__ import annotations

import time
from collections import deque
from threading import Lock
from typing import Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dep
    redis = None  # type: ignore

from .errors import RateLimitedError
from .settings import Settings, get_settings


class _MemoryWindow:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = {}
        self._lock = Lock()

    def hit(self, key: str, window_seconds: int, limit: int) -> bool:
        now = time.monotonic()
        with self._lock:
            dq = self._buckets.setdefault(key, deque())
            while dq and now - dq[0] > window_seconds:
                dq.popleft()
            if len(dq) >= limit:
                return False
            dq.append(now)
            return True


_memory_limiter = _MemoryWindow()


class RateLimiter:
    """Sliding window limiter. Uses Redis when available, falls back to memory."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._redis = None
        if redis is not None:
            try:
                self._redis = redis.from_url(self.settings.redis_url, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None

    @property
    def backend(self) -> str:
        return "redis" if self._redis is not None else "memory"

    def allow(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        if self._redis is not None:
            try:
                count = self._redis.incr(key)
                if count == 1:
                    self._redis.expire(key, window_seconds)
                return count <= limit
            except Exception:
                pass
        return _memory_limiter.hit(key, window_seconds, limit)

    def require(self, key: str, limit: int, window_seconds: int = 60) -> None:
        if not self.allow(key, limit, window_seconds):
            raise RateLimitedError()


_default_limiter: Optional[RateLimiter] = None


def get_limiter() -> RateLimiter:
    global _default_limiter
    if _default_limiter is None:
        _default_limiter = RateLimiter()
    return _default_limiter


def reset_limiter_for_tests() -> None:
    global _default_limiter
    _default_limiter = None
