# Disaster Recovery Plan

> **Owner:** SRE Lead | **Runbook:** [RB-002 `disaster-recovery.md`](../runbooks/disaster-recovery.md) | ADR-0075 (fallback policy) · ADR-0062 (Aurora)

The DR **plan** (this doc) defines targets, topology, and recovery order; the DR **runbook** (RB-002)
is the step-by-step execution. A disaster is declared by the **Tech Lead or SRE Lead** on a full
region outage, production data corruption, or a security shutdown (criteria in RB-002).

---

## 1. Objectives (RPO / RTO)

Authoritative table lives in RB-002 — summarised here:

| Component         | RPO (max data loss)         | RTO (max downtime) |
| ----------------- | --------------------------- | ------------------ |
| api-gateway       | 0 (stateless)               | 5 min              |
| agent-service     | 15 min                      | 15 min             |
| event-consumer    | 0 (Kafka replay)            | 10 min             |
| Database (Aurora) | 1 h (last backup)           | 30 min             |
| Audit log         | 0 (append-only, replicated) | 15 min             |

MTTR target ≤ 1 h (`dora_mttr_target_seconds: 3600`, ADR-0028).

## 2. Topology

- **Multi-AZ by default** (production spans 3 AZs — `terraform/environments/production`); Aurora runs
  1 writer + 2 readers, one per AZ (ADR-0062).
- **Multi-region** is **opt-in** (failover region per RB-002 step 2). When configured, recovery is a
  DNS cutover to the failover region; without it, DR is restore-from-backup in-region.
- State of record is **PostgreSQL + Kafka**; Redis is a cache (degrade-open, ADR-0075), so it is
  rebuilt, not restored.

## 3. Dependency recovery order

Recover bottom-up so each tier's dependencies are healthy first:

```
1. Network / DNS / secrets (Vault, External Secrets)
2. PostgreSQL (Aurora) — restore to RPO; verify encryption key available
3. Redis — start fresh (cache; no restore)
4. Kafka — restore brokers; consumers replay from last committed offset
5. api-gateway, domain-service, event-worker — deploy verified image (canary)
6. Verify Golden Signals + run the smoke suite before reopening traffic
```

The audit log (`audit_events`) must be confirmed writable **before** agent actions resume (the
`db-audit-fallback-blocked` chaos experiment guards this fail-closed behaviour).

## 4. Failover test plan

| Test                              | Cadence             | Pass criterion                                                           |
| --------------------------------- | ------------------- | ------------------------------------------------------------------------ |
| Restore-from-backup drill         | Quarterly           | DB restored within RTO; data within RPO (see `backup-restore-policy.md`) |
| Region failover (if multi-region) | Semi-annual GameDay | DNS cutover + service health within RTO                                  |
| Dependency-order rehearsal        | Quarterly GameDay   | Recovery order in §3 executes cleanly                                    |

Record each drill under `docs/resilience/gamedays/` (evidence for ISO 27001 A.5.30 / SOC 2 A1.2).

## 5. Communication

On DR activation: open an incident (severity matrix), assign an Incident Commander, update the status
page, and notify stakeholders per the incident-response process. Post-DR: a blameless post-mortem is
mandatory.
