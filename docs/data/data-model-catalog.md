# Data Model Catalog

> **Owner:** Tech Lead + DPO | **Authoritative schema:** `alembic/versions/` (migrations) · Avro schemas in `infrastructure/message-broker/schema-registry/avro/`
> **Related:** [`data-classification.md`](data-classification.md) · ADR-0013 (retention) · ADR-0018/0019 (encryption) · `services.yaml` (topics)

A single index of every persisted entity: what it stores, who owns it, where it lives, its highest
PII classification, encryption, retention, and how it is exposed. The migrations remain the
authoritative schema — this catalog summarises and classifies; it does not restate every column.

---

## 1. PostgreSQL tables

Source of truth: `alembic/versions/`. Highest PII level per `specs/privacy/pii-inventory.md`;
retention per ADR-0013; encryption per ADR-0018.

| Table                    | Purpose                                          | Key fields (see migration for full schema)                                                                                              | Highest PII                                 | Encrypted at rest                             | Retention (ADR-0013)                        | Owner                    | Migration                               |
| ------------------------ | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | --------------------------------------------- | ------------------------------------------- | ------------------------ | --------------------------------------- |
| `audit_events`           | Immutable audit trail of agent/system actions    | `id`, `event_type`, `agent_id`, `user_id`, `action`, `outcome`, `metadata`, `trace_id`, `approver_id`, `created_at`                     | L2 (residual in `metadata`)                 | **Yes** — `metadata` (AES-256-GCM)            | Audit logs: 90d hot / 1y warm               | Platform / Security      | `0001_create_audit_events.py`           |
| `agent_memory_documents` | Vector memory (bug history, doc index)           | `id`, `content`, `embedding` (vector), `source`, `tags`, `created_at`                                                                   | L2 (residual in `content`)                  | **Yes** — `content` (AES-256-GCM)             | Bug history TTL 90d (ADR-0017)              | AI Governance            | `0003_create_agent_memory_documents.py` |
| `requests`               | Request pipeline state                           | `id`, `status`, `priority`, `masked_payload`, `result`, `error_message`, `created_at`, `updated_at`                                     | L3 (payload is **masked**)                  | Payload masked pre-store                      | Operational: ≤ 90d                          | Platform                 | `0004_create_requests.py`               |
| `hitl_requests_archive`  | Decided/expired HITL requests (audit)            | `id`, `agent_id`, `action_type`, `action_parameters`, `risk_score`, `context_summary`, `status`, `approver_id`, `rationale`, timestamps | L2 (masked; encrypted in Redis pre-archive) | Masked; Redis copy value-encrypted (ADR-0019) | Agent action history: 90d + 30d soft-delete | Security / AI Governance | `0005_create_hitl_archive.py`           |
| `agent_context_graphs`   | Long-running agent session durability (ADR-0033) | `graph_id`, `session_id`, `root_goal_description`, `status`, `graph_data` (JSONB), timestamps                                           | L3                                          | No (no L1/L2 by design)                       | Tied to session lifecycle                   | AI Governance            | `0006_add_context_graph_table.py`       |

> If a new migration adds a table or a PII-bearing column, add a row here and classify it in
> `specs/privacy/pii-inventory.md` in the same PR (DoR/DoD obligation).

## 2. Redis (ephemeral / cache)

Production: `rediss://` (TLS, ADR-0019). In-memory fallbacks exist for local dev (CLAUDE.md §0.1).

| Key family         | Purpose               | Store class                                  | PII / encryption                            | TTL                   |
| ------------------ | --------------------- | -------------------------------------------- | ------------------------------------------- | --------------------- |
| Request state      | hot request status    | `RedisRequestStore` / `InMemoryRequestStore` | masked payload                              | request lifecycle     |
| HITL requests      | pending approvals     | `HITLRedisStore` / `InMemoryHITLStore`       | **value-encrypted** (AES-256-GCM, ADR-0019) | until decided/expired |
| Session memory     | agent session context | `SessionMemory`                              | masked                                      | session               |
| Rate-limit buckets | throttling            | `slowapi`                                    | none (IP / `sub`)                           | window                |

> A Redis key-naming standard (prefixes, TTL conventions) and TTL-verification tests are a known gap
> — see Wave 4 of the improvement plan. Document the convention here when it lands.

## 3. Kafka topics (event-borne data)

Canonical registry: `services.yaml` `topics:`; channels in `docs/api/asyncapi/v1/asyncapi.yaml`; Avro
schemas in `infrastructure/message-broker/schema-registry/avro/`. **All payloads are PII-masked
before publish** (`specs/api/async-api-design.md`).

| Topic (registry name)      | Producer                | Schema (Avro)                   | Retention        | PII    |
| -------------------------- | ----------------------- | ------------------------------- | ---------------- | ------ |
| `request.created.v1`       | api-gateway             | `request-created-v1.avsc`       | 7d               | masked |
| `hitl.decision.v1`         | api-gateway             | `hitl-decision-v1.avsc`         | 30d              | masked |
| `audit.event.v1`           | api-gateway, batch-jobs | `audit-event-v1.avsc`           | 90d (compliance) | masked |
| `domain.entity.created.v1` | domain-service          | `domain-entity-created-v1.avsc` | 7d               | masked |
| `domain.entity.updated.v1` | domain-service          | `domain-entity-updated-v1.avsc` | 7d               | masked |
| `event.processed.v1`       | event-worker            | `event-processed-v1.avsc`       | 7d               | masked |
| `domain.request.dlq`       | api-gateway             | `domain-request-dlq-v1.avsc`    | 30d (recovery)   | masked |

> **Known gap (tracked):** the registry topic names above use a versioned dotted scheme, while the
> AsyncAPI **channel** names use a different scheme (`domain.request.created`, `agent.action.*`). This
> drift is surfaced by the traceability gate and owned by the Platform team — reconcile before relying
> on a 1:1 topic↔channel mapping.

## 4. Storage backends summary

| Backend    | Holds                | Encryption                                   | Notes                      |
| ---------- | -------------------- | -------------------------------------------- | -------------------------- |
| PostgreSQL | tables in §1         | field-level AES-256-GCM for L1/L2 (ADR-0018) | authoritative store        |
| Redis      | §2 (cache/ephemeral) | TLS + value-encryption for HITL (ADR-0019)   | in-memory fallback for dev |
| Kafka      | §3 (events)          | masked payloads; broker TLS                  | schema-registry governed   |

## 5. Data-subject rights & retention

Erasure/access/portability requests (LGPD + GDPR) operate across the entities in §1–§3. Honour the
ADR-0013 retention caps and `data-classification.md` handling rules; audit/compliance records have
their own legally-mandated retention and are exempt from routine erasure.
