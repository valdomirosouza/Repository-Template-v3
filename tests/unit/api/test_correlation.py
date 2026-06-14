"""Unit tests for the request-correlation middleware.

Spec: docs/api/api-standards.md (§3 Request & correlation IDs)

Builds a minimal app wiring only the correlation middleware (same isolation pattern as
test_requests_router.py — no Kafka/Redis/lifespan). All inputs are obviously synthetic.
"""

from __future__ import annotations

import re

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api.rest.correlation import (
    REQUEST_ID_HEADER,
    install_correlation,
    resolve_request_id,
)

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _make_app() -> FastAPI:
    app = FastAPI()
    install_correlation(app)

    @app.get("/ok")
    async def ok() -> dict[str, bool]:
        return {"ok": True}

    return app


@pytest.mark.unit
class TestCorrelationMiddleware:
    async def test_every_response_has_request_id_header(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=_make_app()), base_url="http://test"
        ) as client:
            response = await client.get("/ok")
        assert response.status_code == 200
        rid = response.headers.get(REQUEST_ID_HEADER)
        assert rid is not None and _UUID.match(rid), f"missing/invalid X-Request-Id: {rid!r}"

    async def test_valid_inbound_request_id_is_echoed(self) -> None:
        supplied = "12345678-1234-1234-1234-1234567890ab"
        async with AsyncClient(
            transport=ASGITransport(app=_make_app()), base_url="http://test"
        ) as client:
            response = await client.get("/ok", headers={REQUEST_ID_HEADER: supplied})
        assert response.headers[REQUEST_ID_HEADER] == supplied

    async def test_garbage_inbound_request_id_is_replaced(self) -> None:
        # Prevents log/response injection via an attacker-controlled header.
        async with AsyncClient(
            transport=ASGITransport(app=_make_app()), base_url="http://test"
        ) as client:
            response = await client.get(
                "/ok", headers={REQUEST_ID_HEADER: "../../etc/passwd\nINJECT"}
            )
        rid = response.headers[REQUEST_ID_HEADER]
        assert rid != "../../etc/passwd\nINJECT"
        assert _UUID.match(rid)


@pytest.mark.unit
class TestResolveRequestId:
    def test_none_mints_uuid(self) -> None:
        assert _UUID.match(resolve_request_id(None))

    def test_valid_uuid_preserved_lowercased(self) -> None:
        assert (
            resolve_request_id("ABCDEF01-1234-1234-1234-1234567890AB")
            == "abcdef01-1234-1234-1234-1234567890ab"
        )

    def test_non_uuid_is_rejected(self) -> None:
        assert resolve_request_id("not-a-uuid") != "not-a-uuid"
        assert _UUID.match(resolve_request_id("not-a-uuid"))
