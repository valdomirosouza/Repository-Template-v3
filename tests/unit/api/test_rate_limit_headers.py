"""Unit test for X-RateLimit-* response headers (slowapi headers_enabled).

Spec: docs/api/api-standards.md (§7 Rate limiting)
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, Request, Response
from httpx import ASGITransport, AsyncClient
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.api.rest._limiter import limiter


def _make_app() -> FastAPI:
    # Mirror main.py's limiter wiring on a minimal app with one limited route.
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)

    @app.get("/limited")
    @limiter.limit("100/minute")
    async def limited(request: Request, response: Response) -> dict[str, bool]:
        return {"ok": True}

    return app


@pytest.mark.unit
class TestRateLimitHeaders:
    async def test_rate_limit_headers_present(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=_make_app()), base_url="http://test"
        ) as client:
            response = await client.get("/limited")
        assert response.status_code == 200
        # headers_enabled=True surfaces the budget so clients can self-throttle.
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "100"
