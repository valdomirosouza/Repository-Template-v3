# Resilience

> **Owner:** SRE Lead | Proving the system recovers **before** a real incident demands it.

Resilience artefacts that tie together the existing DR runbook, chaos experiments, and backup tooling
into reviewable policy.

| Doc                                                          | Covers                                                                                        |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| [`dr-plan.md`](dr-plan.md)                                   | RPO/RTO objectives, topology, dependency recovery order, failover tests (executes via RB-002) |
| [`backup-restore-policy.md`](backup-restore-policy.md)       | Per-storage backup/restore, encryption-key dependency, restore-drill cadence                  |
| [`chaos-experiment-catalog.md`](chaos-experiment-catalog.md) | The 10 Chaos Toolkit experiments, blast-radius policy, GameDay cadence                        |

Related: RB-002 (`docs/runbooks/disaster-recovery.md`), RB-001 (rollback), `tests/chaos/`,
`infrastructure/scripts/db/`, `chaos-smoke.yml`. Drill evidence → `docs/resilience/gamedays/`.
