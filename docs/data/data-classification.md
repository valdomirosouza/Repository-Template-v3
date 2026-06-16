# Data Classification & Handling

> **Owner:** DPO + Security Lead | **Authoritative source of field classification:** [`specs/privacy/pii-inventory.md`](../../specs/privacy/pii-inventory.md)
> **Related:** ADR-0012 (PII masking) · ADR-0013 (retention) · ADR-0018 (DB encryption) · ADR-0019 (Redis TLS + value encryption)

This page does **not** re-define the per-field PII inventory — `specs/privacy/pii-inventory.md` is
authoritative and wins on any conflict. It provides the **cross-cutting handling rules** that follow
from a classification level: what masking, encryption, retention, transport, and logging each level
requires. Use it with [`data-model-catalog.md`](data-model-catalog.md), which classifies each stored
entity.

---

## 1. Classification levels (from `specs/privacy/pii-inventory.md`)

| Level  | Name      | Definition                                      | Example masking tokens       | Retention cap |
| ------ | --------- | ----------------------------------------------- | ---------------------------- | ------------- |
| **L1** | Critical  | Directly identifies a natural person; regulated | `[CPF]`, `[CARD]`            | 90 days       |
| **L2** | Sensitive | Identifies in combination; moderate risk        | `[EMAIL]`, `[PHONE]`, `[IP]` | 1 year        |
| **L3** | Internal  | Technical identifiers; low direct risk          | `[TOKEN]`, `[UUID]`          | 2 years       |
| **L4** | Public    | Publicly available; no masking required         | pass through                 | per policy    |

> If these drift from `pii-inventory.md`, the inventory is correct — open a PR to fix this table.

## 2. Handling rules by level

| Control                                                                   | L1 Critical                      | L2 Sensitive    | L3 Internal                                 | L4 Public  |
| ------------------------------------------------------------------------- | -------------------------------- | --------------- | ------------------------------------------- | ---------- |
| **Mask before log / LLM call** (ADR-0012, `src/guardrails/pii_filter.py`) | Always                           | Always          | Tokenise where feasible                     | No         |
| **Mask before Kafka publish**                                             | Always                           | Always          | Yes                                         | No         |
| **Encrypt at rest** (AES-256-GCM, ADR-0018/0019)                          | Required                         | Required        | Not required (unless co-located with L1/L2) | No         |
| **Encrypt in transit**                                                    | TLS 1.2+ (`rediss://` for Redis) | TLS 1.2+        | TLS 1.2+                                    | TLS 1.2+   |
| **Retention cap** (ADR-0013)                                              | 90 days                          | 1 year          | 2 years                                     | per policy |
| **DPIA/RIPD on new processing**                                           | Required                         | Required        | Assess                                      | No         |
| **Access**                                                                | Least-privilege + audit          | Least-privilege | Role-based                                  | Open       |

## 3. Encryption rule (ADR-0018 / ADR-0019)

- **L1/L2 columns in PostgreSQL** are encrypted with field-level **AES-256-GCM** via the
  `EncryptedField` helper (`src/shared/db_encryption.py`); wire format `enc:v1:<base64(nonce‖ct‖tag)>`.
- **Redis** runs over `rediss://` (TLS) in production; HITL request payloads are **value-encrypted**
  with the same `DB_ENCRYPTION_KEY` before write (`HITLRedisStore` receives an `EncryptedField`).
- Keys live in Vault, injected as `DB_ENCRYPTION_KEY` at pod start; rotation 180 days.
- `Settings.reject_placeholder_secrets` blocks production deploy if `DB_ENCRYPTION_KEY` /
  `REDIS_TLS_ENABLED` are unset (CLAUDE.md §3.2).

## 4. Masking

- All L1–L3 fields are masked at boundaries by `src/guardrails/pii_filter.py` **before** any log
  write, LLM call, or broker publish (CLAUDE.md §3.1, LLM06).
- Masking is tokenised (`[EMAIL]`, `[CPF]`, …) so masked text remains useful for debugging and
  embeddings without re-identifying the subject.

## 5. Obligations

- **New field or new processing** → classify it in `pii-inventory.md`, reflect it in
  `data-model-catalog.md`, and run a **DPIA/RIPD** for L1/L2 (CLAUDE.md §2 Step 5, §3.1).
- **Never** put real PII in code, tests, fixtures, or logs (CLAUDE.md §3.1) — use synthetic data.
- LGPD + GDPR data-subject rights (access, erasure, portability) operate on the entities catalogued
  in `data-model-catalog.md`; honour the retention caps above.
