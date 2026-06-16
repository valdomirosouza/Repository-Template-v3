"""Request correlation middleware.

Assigns every request a stable ``request_id`` (a client-facing correlation id), echoes it as the
``X-Request-Id`` response header, and exposes it — plus the active OTel ``trace_id`` — on
``request.state`` so error handlers can include both in the response body.

Spec: docs/api/api-standards.md (§3 Request & correlation IDs), docs/api/error-model.md
ADR:  ADR-0004 (Observability Stack)
"""

from __future__ import annotations

import re
import uuid

from fastapi import FastAPI
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-Id"

# Only honour a client-supplied request id if it is a UUID. An attacker-controlled header could
# otherwise inject arbitrary text into logs and error bodies (log forging / response injection).
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def resolve_request_id(inbound: str | None) -> str:
    """Echo a valid inbound UUID request id, otherwise mint a fresh one."""
    if inbound and _UUID_RE.match(inbound):
        return inbound.lower()
    return str(uuid.uuid4())


def current_trace_id() -> str | None:
    """The active OTel trace id as 32-hex, or None when there is no valid span."""
    span_ctx = trace.get_current_span().get_span_context()
    return format(span_ctx.trace_id, "032x") if span_ctx.is_valid else None


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Set ``request.state.request_id`` / ``request.state.trace_id`` and the response header."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = resolve_request_id(request.headers.get(REQUEST_ID_HEADER))
        request.state.request_id = request_id
        request.state.trace_id = current_trace_id()
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def install_correlation(app: FastAPI) -> None:
    """Register the correlation middleware. Call last so it is the outermost layer — the
    ``X-Request-Id`` header is then set on every response, including error responses."""
    app.add_middleware(CorrelationIdMiddleware)
