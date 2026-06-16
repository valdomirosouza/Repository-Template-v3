"""Idempotency-Key support for unsafe POST endpoints.

A client may send an ``Idempotency-Key`` header on a retryable POST; the first request is processed
normally and its response cached, and any later request with the same key returns the cached
response **without re-running side effects** (no duplicate event publish / state write). This makes
client retries safe (api-standards.md §6).

Backward-compatible: idempotency only activates when both the header is present AND an
``IdempotencyStore`` is wired on ``app.state``. With no header (or no store), behaviour is the
same as before.

Spec: docs/api/api-standards.md (§6 Idempotency)
"""

from __future__ import annotations

import time
from typing import Protocol

# Default cache lifetime for a stored idempotent response. A client retry window of 24h is a common
# default; tune per endpoint if needed.
DEFAULT_TTL_SECONDS = 86_400


def make_key(route: str, idempotency_key: str) -> str:
    """Namespace the client key by route so the same key on different routes does not collide."""
    return f"idempotency:{route}:{idempotency_key}"


class IdempotencyStore(Protocol):
    """Minimal store contract: get a cached response body, or set one with a TTL."""

    async def get(self, key: str) -> str | None: ...

    async def set(self, key: str, value: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None: ...


class InMemoryIdempotencyStore:
    """Process-local store with TTL — used in tests and local dev without Redis."""

    def __init__(self) -> None:
        self._data: dict[str, tuple[float, str]] = {}

    async def get(self, key: str) -> str | None:
        entry = self._data.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at < time.monotonic():
            self._data.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self._data[key] = (time.monotonic() + ttl_seconds, value)


class RedisIdempotencyStore:
    """Redis-backed store using native key expiry (SET ... EX). Shared across pods."""

    def __init__(self, client: object) -> None:
        # `client` is a redis.asyncio.Redis; typed as object to avoid a hard import here.
        self._client = client

    async def get(self, key: str) -> str | None:
        value = await self._client.get(key)  # type: ignore[attr-defined]
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else str(value)

    async def set(self, key: str, value: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        await self._client.set(key, value, ex=ttl_seconds)  # type: ignore[attr-defined]
