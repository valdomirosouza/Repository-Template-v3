# Structured Logging Schema

> **Owner:** SRE Lead | **Implements against:** `src/observability/logger.py` (`StructuredLogger`) | ADR-0004 (observability) · ADR-0012 (PII masking)

Every log line is structured JSON, PII-masked, and correlated to traces. This page is the **field
contract** behind `StructuredLogger` so logs are queryable and consistent across services and
languages. (The matching golden-signals/OTel guidance is in `skills/sre/golden-signals.md` and
`skills/observability/otel-instrumentation.md`.)

---

## 1. Always-present fields (emitted automatically)

`StructuredLogger._build_record` stamps these on every record:

| Field       | Source                         | Notes                               |
| ----------- | ------------------------------ | ----------------------------------- |
| `timestamp` | ISO-8601 UTC                   | event time                          |
| `severity`  | DEBUG/INFO/WARNING/ERROR/AUDIT | log level                           |
| `service`   | `settings.service_name`        | the service emitting                |
| `component` | logger component               | e.g. `api.requests`                 |
| `message`   | caller                         | human-readable, **no PII**          |
| `trace_id`  | active OTel span (32-hex)      | ties the log to a distributed trace |
| `span_id`   | active OTel span (16-hex)      | the span within the trace           |

## 2. Required context fields (callers add where applicable)

Pass these as `logger.info("...", request_id=..., risk_class=...)`; they are masked (§3) and merged
into the record. Include them whenever the operation has them:

| Field                         | Meaning                                                   | Where it comes from                                                 |
| ----------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------- |
| `request_id`                  | client-facing correlation id                              | `CorrelationIdMiddleware` (`X-Request-Id`); ties log ↔ HTTP request |
| `operation`                   | the logical action (e.g. `submit_request`, `hitl_decide`) | caller                                                              |
| `risk_class`                  | risk tier of the action (e.g. agent autonomy/HITL risk)   | risk scorer / HITL gateway                                          |
| `user_context_classification` | PII class of the data in scope (L1–L4)                    | `specs/privacy/pii-inventory.md`                                    |

> `trace_id` + `request_id` together give end-to-end correlation: REST error body → log → trace →
> downstream event (the event envelope also carries `trace_id`).

## 3. PII masking (mandatory)

- Context is **masked by `pii_filter.py`** before the record is written (`mask=True` when
  `settings.pii_masking_enabled`) — never log raw PII (CLAUDE.md §3.1, LLM06).
- `message` must never contain PII (it is not masked — keep it static/templated).

## 4. Audit vs. operational logs

| Stream      | Method                     | Masking        | Use                                                                                                                                 |
| ----------- | -------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Operational | `debug/info/warning/error` | **masked**     | day-to-day observability                                                                                                            |
| Audit       | `audit(event, ...)`        | **not masked** | legal traceability — identifiers preserved (`approver_id`, `agent_id`); immutable trail via `guardrails/audit_logger.py` (ADR-0026) |

Audit records additionally have their own retention (≥ 7y for financial paths) and the immutable
storage backend — they are **not** routine operational logs.

## 5. Conventions

- One event per log call; put variable data in **fields**, not interpolated into `message` (so it's
  queryable and PII-safe).
- Every 4xx/5xx is logged with `request_id` + `trace_id` and **no PII** (OWASP A09).
- New services in other languages (Java/Go/Node) emit the **same** field names so logs join across the
  stack.
