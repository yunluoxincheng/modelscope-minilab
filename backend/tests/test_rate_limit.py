"""Rate limiter unit tests."""
from __future__ import annotations


def test_in_memory_limiter_blocks_after_limit():
    from app.core.rate_limit import _memory_limiter

    key = "test-rl-block"
    # Drain previous state by using a new key.
    for _ in range(3):
        assert _memory_limiter.hit(key, window_seconds=60, limit=3) is True
    assert _memory_limiter.hit(key, window_seconds=60, limit=3) is False


def test_rate_limit_raises():
    from app.core.errors import RateLimitedError
    from app.core.rate_limit import RateLimiter

    limiter = RateLimiter()
    key = "test-raise-key"
    raised = False
    try:
        for _ in range(150):
            limiter.require(key, limit=3, window_seconds=60)
    except RateLimitedError:
        raised = True
    assert raised
