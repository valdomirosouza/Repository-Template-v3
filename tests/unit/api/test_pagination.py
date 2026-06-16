"""Unit tests for cursor pagination — helpers and the HITL list endpoint.

Spec: docs/api/api-standards.md (§5 Pagination)

Pagination is backward-compatible: the list body stays a JSON array; metadata is in headers.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.agents.hitl_gateway import HITLGateway, HITLRequest
from src.agents.hitl_store import InMemoryHITLStore
from src.api.rest.pagination import decode_cursor, encode_cursor, paginate
from src.api.rest.routers.hitl import router
from src.guardrails.audit_logger import AuditLogger, InMemoryAuditStorage
from src.shared.config import settings


@pytest.mark.unit
class TestCursorHelpers:
    def test_round_trip(self) -> None:
        assert decode_cursor(encode_cursor(42)) == 42

    def test_none_and_empty_are_offset_zero(self) -> None:
        assert decode_cursor(None) == 0
        assert decode_cursor("") == 0

    def test_malformed_cursor_raises(self) -> None:
        # "not-base64!!" is invalid base64; "Zm9v" is base64("foo") which lacks the cursor prefix.
        for bad in ("not-base64!!", "Zm9v"):
            with pytest.raises(ValueError):
                decode_cursor(bad)

    def test_paginate_slices_and_signals_next(self) -> None:
        items = list(range(5))
        page, nxt = paginate(items, limit=2, offset=0)
        assert page == [0, 1]
        assert nxt is not None and decode_cursor(nxt) == 2

    def test_paginate_last_page_has_no_next(self) -> None:
        items = list(range(5))
        page, nxt = paginate(items, limit=2, offset=4)
        assert page == [4]
        assert nxt is None


# ── Endpoint-level ──────────────────────────────────────────────────────────────


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/hitl")
    app.state.hitl_gateway = HITLGateway(
        audit_logger=AuditLogger(InMemoryAuditStorage()), broker=None, store=InMemoryHITLStore()
    )
    return app


def _auth() -> dict[str, str]:
    payload = {
        "sub": "reviewer-01",
        "role": "hitl-operator",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return {
        "Authorization": f"Bearer {jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)}"
    }


async def _seed(gateway: HITLGateway, n: int) -> None:
    now = datetime.now(UTC)
    for _ in range(n):
        await gateway.submit_for_approval(
            HITLRequest(
                request_id=str(uuid.uuid4()),
                agent_id="agent-test",
                action_type="test_action",
                action_parameters={},
                risk_score=0.5,
                context_summary="synthetic",
                created_at=now,
                expires_at=now + timedelta(hours=1),
            )
        )


@pytest.mark.unit
class TestHITLListPagination:
    async def test_first_page_array_body_with_headers(self) -> None:
        app = _make_app()
        await _seed(app.state.hitl_gateway, 3)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/hitl/requests?limit=2", headers=_auth())
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list) and len(body) == 2  # body stays an array (non-breaking)
        assert response.headers["X-Limit"] == "2"
        assert response.headers["X-Total-Returned"] == "2"
        assert "X-Next-Cursor" in response.headers  # more remain

    async def test_following_cursor_returns_remainder_without_next(self) -> None:
        app = _make_app()
        await _seed(app.state.hitl_gateway, 3)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            first = await client.get("/hitl/requests?limit=2", headers=_auth())
            cursor = first.headers["X-Next-Cursor"]
            second = await client.get(f"/hitl/requests?limit=2&cursor={cursor}", headers=_auth())
        assert second.status_code == 200
        assert len(second.json()) == 1
        assert "X-Next-Cursor" not in second.headers  # last page

    async def test_invalid_cursor_is_400(self) -> None:
        app = _make_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/hitl/requests?cursor=not-a-valid-cursor", headers=_auth())
        assert response.status_code == 400
