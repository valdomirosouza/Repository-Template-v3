"""Typed domain errors and a backward-compatible structured error model.

Error bodies are a **superset** of the legacy ``{"detail": ...}`` shape: they keep ``detail`` and
the ``application/json`` content-type — preserving the frontend Pact contract
(``tests/contract/pacts/frontend-api_gateway.json``) — while ADDING the RFC 7807 members
(``type``, ``title``, ``status``, ``instance``) and correlation ids (``request_id``, ``trace_id``).

Full RFC 7807 ``application/problem+json`` is intentionally deferred: switching the content-type
is a breaking change for the frontend consumer and belongs to a ``/v2`` API bump (ADR-0024). See
``docs/api/error-model.md``.

Spec: docs/api/error-model.md, docs/api/api-standards.md
"""

from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

# Base URI for error `type` slugs — stable identifiers, versioned with the API (ADR-0024).
# Replace the host at template-init time; the path segment is the contract.
_ERROR_TYPE_BASE = "https://errors.example.com/"


class DomainError(Exception):
    """Base for typed domain errors that map to an HTTP error response.

    Subclasses set ``status``/``error_type``/``title``. Routers may raise these instead of
    ``HTTPException`` for a clearer domain vocabulary; both are reshaped by the handlers below.
    """

    status: int = HTTPStatus.INTERNAL_SERVER_ERROR
    error_type: str = "about:blank"
    title: str = "Internal Server Error"

    def __init__(self, detail: str | None = None, *, headers: dict[str, str] | None = None) -> None:
        self.detail = detail or self.title
        self.headers = headers
        super().__init__(self.detail)


class NotFoundError(DomainError):
    """Resource does not exist or is not visible to the caller (avoid IDOR oracles)."""

    status = HTTPStatus.NOT_FOUND
    error_type = _ERROR_TYPE_BASE + "not-found"
    title = "Resource not found"


class ConflictError(DomainError):
    """Request conflicts with current resource state (e.g. already decided)."""

    status = HTTPStatus.CONFLICT
    error_type = _ERROR_TYPE_BASE + "conflict"
    title = "State conflict"


class AuthorizationError(DomainError):
    """Authenticated but not permitted to perform the action (OWASP A01)."""

    status = HTTPStatus.FORBIDDEN
    error_type = _ERROR_TYPE_BASE + "forbidden"
    title = "Forbidden"


def _reason(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Error"


def build_problem(
    request: Request,
    *,
    status_code: int,
    detail: object,
    title: str | None = None,
    error_type: str | None = None,
) -> dict[str, object]:
    """Build the structured error body (a superset of ``{"detail": ...}``).

    ``request_id``/``trace_id`` come from the correlation middleware via ``request.state``; if the
    middleware did not run (e.g. an error before it), a fresh ``request_id`` is minted so the field
    is never empty.
    """
    request_id: str = getattr(request.state, "request_id", None) or str(uuid.uuid4())
    trace_id: str | None = getattr(request.state, "trace_id", None)
    return {
        "type": error_type or "about:blank",
        "title": title or _reason(status_code),
        "status": status_code,
        "detail": detail,
        "instance": request.url.path,
        "request_id": request_id,
        "trace_id": trace_id,
    }


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Render a typed ``DomainError`` as a structured error response."""
    status_code = int(exc.status)
    body = build_problem(
        request,
        status_code=status_code,
        detail=exc.detail,
        title=exc.title,
        error_type=exc.error_type,
    )
    return JSONResponse(status_code=status_code, content=body, headers=exc.headers)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Reshape a raised ``HTTPException`` into the structured body, preserving its detail,
    status, and headers (e.g. ``Retry-After``, ``WWW-Authenticate``)."""
    body = build_problem(request, status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code, content=body, headers=getattr(exc, "headers", None)
    )


def install_error_handlers(app: FastAPI) -> None:
    """Register the structured error handlers.

    The FastAPI/Starlette default ``RequestValidationError`` (422) handler is intentionally left in
    place — its ``{"detail": [...]}`` shape is part of the consumer contract; the correlation
    middleware still adds ``X-Request-Id`` to those responses.
    """
    app.add_exception_handler(DomainError, domain_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
