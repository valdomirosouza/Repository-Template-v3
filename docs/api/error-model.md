# API Error Model

> **Owner:** Platform / Tech Lead | **Applies to:** all REST endpoints under `/v1/` (`src/api/rest/`)
> **Related:** [`api-standards.md`](api-standards.md) · ADR-0024 (versioning) · `specs/api/async-api-design.md` (events)

A consistent, machine-parseable error contract so clients can handle failures uniformly and every
4xx/5xx is traceable (OWASP A09). This document records the **current** behaviour honestly and
defines the **target** standard; the gap between them is tracked in [§5](#5-conformance--gaps).

---

## 1. Current state (as implemented)

Today the API returns FastAPI's default error shape:

```json
{ "detail": "Request 123 not found." }
```

- Validation errors (`422`) use FastAPI/Pydantic's structured `detail` array.
- `src/api/rest/auth.py` returns `401` with a `WWW-Authenticate: Bearer` header.
- `src/api/rest/routers/requests.py` returns `503` with a `Retry-After` header on capacity exhaustion.
- The one typed domain exception is `HITLGatewayError` (`src/agents/hitl_gateway.py`), mapped to `404`
  in `src/api/rest/routers/hitl.py`.
- **No** `request_id` / `trace_id` is currently included in error bodies.

## 2. Target standard — RFC 7807 Problem Details

New and refactored endpoints SHOULD return [RFC 7807](https://www.rfc-editor.org/rfc/rfc7807)
`application/problem+json`:

```json
{
  "type": "https://errors.example.com/request-not-found",
  "title": "Request not found",
  "status": 404,
  "detail": "Request 123 not found.",
  "instance": "/v1/requests/123",
  "request_id": "01J...",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

| Field        | Required        | Meaning                                                                         |
| ------------ | --------------- | ------------------------------------------------------------------------------- |
| `type`       | yes             | Stable URI identifying the error class (dereferenceable doc, or a URN)          |
| `title`      | yes             | Short, human-readable summary — **constant per `type`** (no variable data)      |
| `status`     | yes             | HTTP status code (mirrors the response line)                                    |
| `detail`     | no              | Human-readable, instance-specific explanation — **never leak PII or internals** |
| `instance`   | no              | URI of the specific occurrence (the request path)                               |
| `request_id` | yes (extension) | Correlation id; also returned in the `X-Request-Id` response header             |
| `trace_id`   | yes (extension) | W3C trace id, ties the error to a distributed trace                             |

## 3. Status code conventions

| Code  | When                                  | Notes                                                             |
| ----- | ------------------------------------- | ----------------------------------------------------------------- |
| `400` | Malformed request the client can fix  |                                                                   |
| `401` | Missing/invalid credentials           | `WWW-Authenticate: Bearer`                                        |
| `403` | Authenticated but not authorised      | ownership/role checks (OWASP A01)                                 |
| `404` | Resource not found / not owned        | do not distinguish "not found" vs "not yours" (avoid IDOR oracle) |
| `409` | State conflict (e.g. already decided) |                                                                   |
| `422` | Validation error                      | Pydantic field errors                                             |
| `429` | Rate limited                          | `Retry-After` (see `api-standards.md`)                            |
| `503` | Capacity/dependency unavailable       | `Retry-After`                                                     |

Default to `5xx` only for genuine server faults; never use `200` with an error body.

## 4. Typed domain errors → problem mapping

Map domain exceptions to a `type` + status at the boundary (one place: an exception handler), not
ad-hoc per route. Recommended hierarchy:

```
DomainError                      → 4xx by subtype
├── NotFoundError                → 404  type: .../not-found
├── ConflictError                → 409  type: .../conflict
├── AuthorizationError           → 403  type: .../forbidden
└── HITLGatewayError (existing)  → 404/409 depending on cause
```

Rules:

- **Never** surface stack traces, SQL, internal hostnames, or PII in `detail` (CLAUDE.md §3.1, A09).
- Log the full error server-side with `request_id` + `trace_id`; return only the safe projection.
- Each `type` is versioned with the API (`/v1/`); changing a `type`'s meaning is a breaking change (ADR-0024).

## 5. Conformance & gaps

| Capability                                         | Status                                               | Owner    |
| -------------------------------------------------- | ---------------------------------------------------- | -------- |
| RFC 7807 `problem+json` shape                      | **Gap** — currently `{"detail": …}`                  | Platform |
| `request_id` in error body + `X-Request-Id` header | **Gap** — not emitted today                          | Platform |
| `trace_id` correlation in errors                   | **Gap** — present in event envelope, not REST errors | Platform |
| Central exception handler → problem mapping        | **Gap** — errors raised per-route                    | Platform |
| `401`/`403`/`404`/`422`/`429`/`503` semantics      | **Implemented**                                      | —        |

Adopt incrementally: add the central handler + correlation middleware first (closes three gaps at
once), then migrate routes. Track adoption in the owning feature spec; do not claim conformance until
the handler exists.
