"""Unit tests for Idempotency-Key support — store and the POST /v1/requests replay.

Spec: docs/api/api-standards.md (§6 Idempotency)
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.agents.request_store import InMemoryRequestStore
from src.api.rest.idempotency import InMemoryIdempotencyStore, make_key
from src.api.rest.routers.requests import router
from src.shared.broker import InMemoryBroker


@pytest.mark.unit
class TestInMemoryIdempotencyStore:
    async def test_set_then_get_returns_value(self) -> None:
        store = InMemoryIdempotencyStore()
        await store.set("k", "v")
        assert await store.get("k") == "v"

    async def test_missing_key_returns_none(self) -> None:
        assert await InMemoryIdempotencyStore().get("absent") is None

    async def test_expired_entry_returns_none(self) -> None:
        store = InMemoryIdempotencyStore()
        await store.set("k", "v", ttl_seconds=-1)  # already expired
        assert await store.get("k") is None

    def test_make_key_namespaces_by_route(self) -> None:
        assert make_key("POST:/a", "x") != make_key("POST:/b", "x")


# ── Endpoint-level ──────────────────────────────────────────────────────────────


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/v1")
    app.state.request_store = InMemoryRequestStore()
    app.state.broker = InMemoryBroker()
    app.state.idempotency_store = InMemoryIdempotencyStore()
    return app


@pytest.mark.unit
class TestIdempotentSubmit:
    async def test_same_key_replays_same_request_id(self) -> None:
        app = _make_app()
        headers = {"Idempotency-Key": "11111111-1111-1111-1111-111111111111"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            first = await client.post(
                "/v1/requests", json={"request_text": "do a thing"}, headers=headers
            )
            second = await client.post(
                "/v1/requests", json={"request_text": "do a thing"}, headers=headers
            )
        assert first.status_code == 202 and second.status_code == 202
        # Replay returns the cached response — identical request_id (a fresh uuid4 each real call).
        assert first.json()["request_id"] == second.json()["request_id"]

    async def test_different_keys_create_distinct_requests(self) -> None:
        app = _make_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            a = await client.post(
                "/v1/requests", json={"request_text": "x"}, headers={"Idempotency-Key": "key-aaaa"}
            )
            b = await client.post(
                "/v1/requests", json={"request_text": "x"}, headers={"Idempotency-Key": "key-bbbb"}
            )
        assert a.json()["request_id"] != b.json()["request_id"]

    async def test_no_key_behaves_as_before(self) -> None:
        app = _make_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            a = await client.post("/v1/requests", json={"request_text": "x"})
            b = await client.post("/v1/requests", json={"request_text": "x"})
        assert a.status_code == 202 and b.status_code == 202
        assert a.json()["request_id"] != b.json()["request_id"]  # no caching without the header
