# Redis Key-Naming & TTL Standard

> **Owner:** Platform / SRE | **Companion:** [`data-model-catalog.md`](data-model-catalog.md) (§2 Redis)
> **Verified by:** `tests/unit/storage/test_ttl_verification.py`

Every Redis key in this system follows one convention so keys are self-describing, collision-free,
and never immortal. This documents the **actual** prefixes and TTLs in the code (not an aspiration).

---

## 1. The convention

```
<domain>:<type>:<id>[:<sub>]
```

- **Lowercase**, colon-delimited segments; the first segment namespaces the owning domain.
- **Every key has a TTL** (or is a member of a TTL'd structure). No unbounded keys — Redis is a
  cache/working store here, not the system of record (PostgreSQL is).
- TTLs are **settings-driven** (`src/shared/config.py`), never hard-coded at the call site.

## 2. Key families in use

| Key pattern                           | Owner                   | Set via                                   | TTL (setting)                               | Default       |
| ------------------------------------- | ----------------------- | ----------------------------------------- | ------------------------------------------- | ------------- |
| `request:state:<request_id>`          | `RedisRequestStore`     | `SET … EX`                                | `request_result_ttl_hours` × 3600           | 24 h          |
| `hitl:req:<request_id>`               | `HITLRedisStore`        | `SET … EX` (🔒 encrypted)                 | `expires_at` + `hitl_redis_ttl_grace_hours` | expiry + 24 h |
| `hitl:pending`                        | `HITLRedisStore`        | `ZADD` (sorted set, score = `expires_at`) | members pruned on read/expiry               | —             |
| `hitl:expired:<request_id>`           | `HITLRedisStore`        | `SET … EX` (🔒 encrypted)                 | `hitl_expired_ttl_days`                     | 7 d           |
| `agent:session:<session_id>:<key>`    | `SessionMemory`         | `SETEX`                                   | `memory_session_ttl_seconds`                | 24 h          |
| `agent:session:<session_id>:__keys__` | `SessionMemory`         | `SADD` + `EXPIRE`                         | `memory_session_ttl_seconds`                | 24 h          |
| `idempotency:<route>:<key>`           | `RedisIdempotencyStore` | `SET … EX`                                | `DEFAULT_TTL_SECONDS`                       | 24 h          |
| `LIMITER/*`                           | slowapi                 | internal                                  | per rate window                             | window        |

> 🔒 = value encrypted at rest with AES-256-GCM before write (ADR-0019). Prefixes for the first four
> families come from settings (`request_redis_key_prefix`, `hitl_redis_key_prefix`) so they can be
> namespaced per environment/tenant.

## 3. Rules for new keys

1. Pick a **domain prefix** (reuse an existing one where it fits; add a setting if it should be
   configurable, like `*_redis_key_prefix`).
2. **Always set a TTL** — choose the setting that bounds the data's useful life; align long-lived
   data with the ADR-0013 retention caps.
3. **Encrypt L1/L2 values** before writing (`EncryptedField`) — never store unmasked PII in Redis
   (CLAUDE.md §3.1; ADR-0019). In production, Redis must be `rediss://` (TLS).
4. **No key without an owner** — add a row to §2 in the same PR.

## 4. Production posture

- TLS (`rediss://`, `redis_tls_enabled=true`) is required in production (ADR-0019).
- RDB snapshots are enabled in local compose (`--save 60 1`); see
  `infrastructure/scripts/db/backup.sh`. Redis is recoverable but is **not** the source of truth —
  request/HITL/audit records of record live in PostgreSQL.
