# Backup & Restore Policy

> **Owner:** SRE Lead + DevOps Lead | **Local tooling:** [`infrastructure/scripts/db/`](../../infrastructure/scripts/db/) | ADR-0013 (retention) · ADR-0018/0019 (encryption)

What is backed up, how often, how it is restored, and how restores are **proven**. A backup that has
never been restored is a hope, not a control — so restore drills are mandatory (§4).

---

## 1. Per-storage policy

| Store                   | What                  | Method                                                                       | Frequency                            | Retention                         | RPO         |
| ----------------------- | --------------------- | ---------------------------------------------------------------------------- | ------------------------------------ | --------------------------------- | ----------- |
| **PostgreSQL (Aurora)** | system of record      | automated snapshots + PITR; `pg_dump` for local/dev (`scripts/db/backup.sh`) | continuous (PITR) / nightly snapshot | per ADR-0013 (audit ≥ 7y)         | ≤ 1 h       |
| **Redis**               | cache / working store | RDB snapshot (`--save 60 1`); `scripts/db/backup.sh`                         | rolling                              | short — **rebuilt, not restored** | n/a (cache) |
| **Kafka**               | event log             | broker replication + retention (`services.yaml` topics)                      | continuous                           | per-topic (7–90 d)                | 0 (replay)  |
| **Audit log**           | compliance record     | within PostgreSQL; append-only, replicated                                   | continuous                           | ≥ 7 y (ADR-0026)                  | 0           |

## 2. Encryption-key dependency (critical)

`audit_events` / `agent_memory_documents` and the Redis HITL payloads are **encrypted at rest**
(AES-256-GCM, ADR-0018/0019). A data backup is **unreadable without the `DB_ENCRYPTION_KEY`** — so the
key must be backed up **separately** (Vault, with its own rotation/recovery), never alongside the
data. Losing the key = losing the data even with a perfect backup.

## 3. Local backup/restore (dev / dev-like)

```bash
infrastructure/scripts/db/backup.sh [OUTPUT_DIR]     # pg_dump + Redis RDB
infrastructure/scripts/db/restore.sh <pg.sql.gz> [redis.rdb]   # DESTRUCTIVE; confirms before applying
```

Production backup is the managed-service responsibility (Aurora automated backups + PITR); these
scripts are for local/dev parity, not production DR.

## 4. Restore-drill cadence (proof)

| Drill                                     | Cadence                               | Evidence                                |
| ----------------------------------------- | ------------------------------------- | --------------------------------------- |
| Local restore (`restore.sh` round-trip)   | Per PR touching storage/migrations    | green `make smoke` after restore        |
| Aurora PITR restore to a scratch instance | Quarterly                             | restored within RTO; data within RPO    |
| Full DR restore rehearsal                 | Quarterly GameDay (with `dr-plan.md`) | dependency order §3 of dr-plan executes |

Record each drill under `docs/resilience/gamedays/<date>-restore.md` (ISO 27001 A.8.13 evidence). A
failed or skipped drill is an incident-worthy finding.

## 5. Obligations

- Every new stateful store added (a table, a new Redis key family, a topic) **must** get a row in §1
  in the same PR (mirrors the `data-model-catalog.md` obligation).
- Backups inherit the data's PII classification — treat backup storage as L1/L2 (encrypted, access
  audited).
