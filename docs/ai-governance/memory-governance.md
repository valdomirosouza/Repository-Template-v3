# Agent Memory Governance

> **Owner:** AI Governance Lead + DPO | **Implements against:** `src/memory/` · `agent_memory_documents` table | ADR-0017 (agent memory) · ADR-0013 (retention)

Agent memory (session memory, the vector store, and `BugHistoryStore` of past HITL rejections) is
persisted data that influences future agent behaviour — so it needs the same governance as any other
data store, plus protection against **memory poisoning**.

---

## 1. Retention

| Memory                    | Store                                     | Retention                                           |
| ------------------------- | ----------------------------------------- | --------------------------------------------------- |
| Session memory            | Redis `agent:session:*` (`SessionMemory`) | `memory_session_ttl_seconds` (24h default)          |
| Vector docs / bug history | `agent_memory_documents` (pgvector)       | `memory_docs_retention_days` (90d, aligns ADR-0013) |

Retention is enforced by TTL (Redis) and is policy for the table (ADR-0013). See
`docs/data/redis-key-naming.md` and the [`data-model-catalog.md`](../data/data-model-catalog.md).

## 2. PII classification & encryption

- Memory content is **PII-masked before write/embed** (`pii_filter.py`) and the `content` column is
  **encrypted at rest** (AES-256-GCM, ADR-0018). Highest class: **L2** (residual after masking).
- Memory is treated as L1/L2 for access purposes — least-privilege, access-audited.

## 3. Deletion workflow (data-subject rights)

- Erasure requests (LGPD/GDPR) must purge a subject's traces from session memory and
  `agent_memory_documents`. Because content is masked, deletion is keyed by `agent_id`/`session_id` /
  document `source`, not by re-identifying the subject.
- Audit/compliance memory has its own legally-mandated retention and is exempt from routine erasure
  (document the exemption).

## 4. Memory poisoning detection

A retrieval store is an attack surface: a malicious or low-quality document, once indexed, biases
future agents.

- **Provenance:** only index trusted sources (`specs/`, `docs/adr/` via `DocumentIndexer`) — never
  untrusted user input.
- **Bug-history integrity:** `BugHistoryStore` records HITL **rejections** (negative examples) — verify
  entries originate from real audited rejection events, not injected.
- **Anomaly signal:** monitor for sudden shifts in retrieved-context distribution / agent behaviour;
  a spike is a poisoning indicator → review + purge.

## 5. Versioning & audit

- **Versioning:** record the embedding model + chunking version with the index; a change forces a
  re-index (`rag-quality.md` §5).
- **Access audit:** memory reads/writes by agents are audit-logged (`guardrails/audit_logger.py`,
  immutable) — every retrieval that influenced an action is traceable.
