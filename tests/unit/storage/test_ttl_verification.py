"""TTL + key-naming verification for the Redis-backed stores.

Spec: docs/data/redis-key-naming.md

Guards the invariant that every Redis key has a TTL (no immortal keys) and follows the
``<domain>:<type>:<id>`` convention. Uses fakeredis (no real Redis), matching test_session_memory.py.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import fakeredis.aioredis
import pytest

from src.agents.hitl_gateway import HITLRequest
from src.agents.hitl_store import HITLRedisStore
from src.agents.request_store import RedisRequestStore, RequestState
from src.api.rest.idempotency import RedisIdempotencyStore, make_key
from src.memory.session_memory import SessionMemory
from src.shared.config import settings


@pytest.fixture()
async def redis():
    server = fakeredis.aioredis.FakeRedis()
    yield server
    await server.aclose()


@pytest.mark.unit
class TestRequestStoreTTL:
    async def test_state_key_has_ttl_and_naming(self, redis) -> None:
        store = RedisRequestStore(redis)
        now = datetime.now(UTC)
        await store.save(
            RequestState(request_id="req-1", status="queued", created_at=now, updated_at=now)
        )
        key = f"{settings.request_redis_key_prefix}:state:req-1"
        ttl = await redis.ttl(key)
        assert 0 < ttl <= settings.request_result_ttl_hours * 3600


@pytest.mark.unit
class TestSessionMemoryTTL:
    async def test_session_key_has_ttl_and_naming(self, redis) -> None:
        memory = SessionMemory(redis)
        await memory.set("sess-1", "sprint_id", "sprint-42")
        ttl = await redis.ttl("agent:session:sess-1:sprint_id")
        assert 0 < ttl <= settings.memory_session_ttl_seconds


@pytest.mark.unit
class TestIdempotencyStoreTTL:
    async def test_key_has_requested_ttl(self, redis) -> None:
        store = RedisIdempotencyStore(redis)
        key = make_key("POST:/v1/requests", "abc")
        await store.set(key, '{"x":1}', ttl_seconds=120)
        ttl = await redis.ttl(key)
        assert 0 < ttl <= 120
        assert key.startswith("idempotency:")


@pytest.mark.unit
class TestHITLStoreTTL:
    async def test_req_key_has_ttl_beyond_expiry(self, redis) -> None:
        store = HITLRedisStore(client=redis, encryption=None)
        now = datetime.now(UTC)
        req = HITLRequest(
            request_id="hitl-1",
            agent_id="agent-test",
            action_type="test_action",
            action_parameters={},
            risk_score=0.5,
            context_summary="synthetic",
            created_at=now,
            expires_at=now + timedelta(hours=1),
        )
        await store.save(req)
        key = f"{settings.hitl_redis_key_prefix}:req:hitl-1"
        ttl = await redis.ttl(key)
        # TTL = remaining-to-expiry (~1h) + grace; comfortably positive and below 2h + grace.
        assert ttl > 0
        assert ttl <= 3600 + settings.hitl_redis_ttl_grace_hours * 3600 + 5
