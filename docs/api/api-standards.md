# REST API Standards

> **Owner:** Platform / Tech Lead | **Applies to:** all REST endpoints under `/v1/` (`src/api/rest/`)
> **Related:** ADR-0024 (versioning) · [`error-model.md`](error-model.md) · `specs/api/async-api-design.md` (events) · `docs/api/openapi/v1/openapi.yaml` (the contract)

The conventions every REST endpoint follows. The OpenAPI document is the **contract**; this page is
the **policy** behind it. Where a standard is not yet implemented it is marked **(target)** with the
gap owned in [§9](#9-conformance--gaps) — no aspirational claim is presented as current fact.

---

## 1. Versioning (ADR-0024)

- **URL major version:** `/v1/…`. Breaking changes ship under a new prefix (`/v2/`).
- **Breaking** = remove/rename a field, change a type, make an optional field required, remove an
  endpoint, change a status code or auth requirement. **Non-breaking** = add an optional field, a new
  endpoint, or expand an enum.
- **Deprecation:** `Deprecation` + `Sunset` response headers (RFC 8594); old version supported ≥ 2
  sprints after the successor ships.

## 2. Authentication & authorisation

- **Mechanism:** JWT Bearer (`Authorization: Bearer <jwt>`), validated in `src/api/rest/auth.py`
  (HS256 default; RS256/ES256 for multi-service). `require=['exp','sub']`.
- **Identity from the token, never the body:** e.g. `approver_id` comes from the JWT `sub`
  (REM-001), never a request field.
- **Authorisation:** role checks via dependencies (e.g. `require_hitl_operator`). Enforce ownership
  on every resource access — no IDOR (OWASP A01). Document the required role/scope **per endpoint** in
  the OpenAPI `security` block.

## 3. Request & correlation IDs

- Every request gets a `request_id`; echo it back as `X-Request-Id` and include it in logs and error
  bodies (see `error-model.md`).
- Propagate W3C `traceparent`; the `trace_id` ties REST calls to the event envelope's `trace_id`
  (`specs/api/async-api-design.md`) and to OTel spans.
- **Implemented:** `CorrelationIdMiddleware` (`src/api/rest/correlation.py`) sets `X-Request-Id` on
  every response and exposes `request.state.request_id`/`trace_id` to handlers. A client-supplied
  `X-Request-Id` is honoured only if it is a UUID (otherwise replaced — prevents log/response injection).

## 4. Errors

Use the shared error model — see [`error-model.md`](error-model.md). Status-code semantics, the RFC
7807 target shape, and the typed-exception mapping live there; do not invent per-route error shapes.

## 5. Pagination **(target)**

List endpoints SHOULD NOT return unbounded arrays (today `/v1/hitl/requests` does — §9). Standard:

- **Cursor-based** for large/streaming collections: `?limit=` (default 50, max 200) + `?cursor=`;
  return `next_cursor` (null at end).
- Envelope: `{ "items": [...], "next_cursor": "...", "limit": 50 }`.
- Offset pagination (`?offset=`) only for small, stable admin lists.

## 6. Idempotency **(target)**

- Unsafe, retryable POSTs SHOULD accept an `Idempotency-Key` header; the same key returns the same
  result within a TTL window (store keyed by `(route, key)`).
- `POST /v1/requests` is naturally idempotent only in that it mints a new id per call — that is **not**
  retry-safe; an `Idempotency-Key` is the standard fix (§9).

## 7. Rate limiting

- Implemented via `slowapi` (`src/api/rest/_limiter.py`); per-JWT-`sub` bucket, falling back to client
  IP. Limit: `rate_limit_requests_per_minute`.
- Return `429` on limit; capacity exhaustion returns `503`. Both SHOULD carry `Retry-After`.
- **(target)** Emit `X-RateLimit-Limit` / `X-RateLimit-Remaining` headers (not present today — §9).

## 8. Payloads & validation

- JSON only; `snake_case` field names; timestamps ISO-8601 UTC (`...Z`).
- Validate every field at the boundary with Pydantic; reject unknown fields where practical.
- **Never** return PII in responses, logs, or errors beyond what the caller is entitled to; mask per
  `specs/privacy/pii-inventory.md` (CLAUDE.md §3.1).
- Document an example request + response for every operation in OpenAPI.

## 9. Conformance & gaps

| Standard                                         | Status                                                     | Owner    |
| ------------------------------------------------ | ---------------------------------------------------------- | -------- |
| URL versioning `/v1/` (ADR-0024)                 | **Implemented**                                            | —        |
| JWT Bearer auth, identity-from-token             | **Implemented**                                            | —        |
| Per-endpoint `security` documented in OpenAPI    | **Partial** — verify each op                               | Platform |
| `X-Request-Id` + correlation middleware          | **Implemented** — `src/api/rest/correlation.py`            | —        |
| `trace_id` in REST errors                        | **Implemented** — structured error body                    | —        |
| Structured error body + typed domain errors      | **Implemented** — `src/api/rest/errors.py`                 | —        |
| Pagination on list endpoints                     | **Gap** — `/v1/hitl/requests` unbounded                    | Platform |
| `Idempotency-Key` on unsafe POSTs                | **Gap**                                                    | Platform |
| `X-RateLimit-*` headers                          | **Gap** (limiting works; headers absent)                   | Platform |
| RFC 7807 `application/problem+json` content-type | **Deferred** — `/v2` bump (ADR-0024); see `error-model.md` | Platform |

Each gap should be closed under a referenced spec/ADR, not silently. Until then, this page is the
agreed **target** — implementers must not assume a gap is already satisfied.
