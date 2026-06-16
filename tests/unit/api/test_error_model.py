"""Unit tests for the structured error model (typed DomainError + HTTPException reshaping).

Spec: docs/api/error-model.md

Verifies the backward-compatible superset: `detail` and `application/json` are preserved (frontend
Pact contract) while the structured + correlation fields are added.
"""

from __future__ import annotations

import re

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from src.api.rest.correlation import REQUEST_ID_HEADER, install_correlation
from src.api.rest.errors import NotFoundError, install_error_handlers

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_SUPERSET_FIELDS = ("type", "title", "status", "detail", "instance", "request_id", "trace_id")


def _make_app() -> FastAPI:
    app = FastAPI()
    install_correlation(app)
    install_error_handlers(app)

    @app.get("/boom-domain")
    async def boom_domain() -> None:
        raise NotFoundError("widget 42 not found")

    @app.get("/boom-http")
    async def boom_http() -> None:
        raise HTTPException(status_code=503, detail="busy", headers={"Retry-After": "5"})

    return app


@pytest.mark.unit
class TestDomainError:
    async def test_typed_error_renders_structured_404(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=_make_app()), base_url="http://test"
        ) as client:
            response = await client.get("/boom-domain")
        assert response.status_code == 404
        # Backward-compat: content-type stays application/json (not problem+json).
        assert "application/json" in response.headers.get("content-type", "")
        body = response.json()
        for field in _SUPERSET_FIELDS:
            assert field in body, f"missing structured field {field!r}"
        assert body["detail"] == "widget 42 not found"  # legacy field preserved
        assert body["status"] == 404
        assert body["type"].endswith("/not-found")
        assert body["instance"] == "/boom-domain"

    async def test_request_id_in_body_matches_header(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=_make_app()), base_url="http://test"
        ) as client:
            response = await client.get("/boom-domain")
        rid = response.json()["request_id"]
        assert _UUID.match(rid)
        assert response.headers[REQUEST_ID_HEADER] == rid


@pytest.mark.unit
class TestHTTPExceptionReshaping:
    async def test_http_exception_keeps_detail_status_and_headers(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=_make_app()), base_url="http://test"
        ) as client:
            response = await client.get("/boom-http")
        assert response.status_code == 503
        assert response.headers.get("Retry-After") == "5"  # original header preserved
        body = response.json()
        assert body["detail"] == "busy"  # legacy consumers still work
        assert body["status"] == 503
        for field in _SUPERSET_FIELDS:
            assert field in body
