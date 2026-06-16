# Repository Traceability Matrix

> **Owner:** Tech Lead + SRE Lead · **Status:** Living document · **Last updated:** 2026-06-14
>
> This matrix makes every declared service traceable across its governing artefacts:
> **service → spec → ADR → API contract → SLO → runbook → dashboard → tests**. It is the
> human-facing companion to the machine-enforced gates in `scripts/governance/` (run them with
> `make verify-traceability`). When a cell says “—”, the artefact does not exist yet and the gap is
> listed in [§4 Known Gaps](#4-known-gaps).

The canonical source of services, ADRs, and topics is [`services.yaml`](../../services.yaml)
(CLAUDE.md §0.1). This document derives from it; the scripts below fail CI if the registry and the
artefacts on disk diverge.

---

## 1. Enforcement (run locally + in CI)

| Gate                           | Script                                          | What it proves                                                                                                                                                               | Mode                                                                                                            |
| ------------------------------ | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `make check-traceability`      | `scripts/governance/check_traceability.py`      | Every ADR a service cites exists; every published/subscribed topic is defined, has an Avro schema file, and is referenced in AsyncAPI; every `depends_on` is a real service. | ADR/topic/schema/dependency = **blocking**; AsyncAPI naming = **report mode** (`STRICT=1` to block — ADR-0070). |
| `make check-service-slo-files` | `scripts/governance/check_service_slo_files.py` | Every canary-deployed (`type: api`/`frontend`) service has a valid `docs/sre/slo/<service>.yaml` canary block; `worker`/`job` are explicitly exempt.                         | **Blocking** (ADR-0073).                                                                                        |
| `make check-runbook-links`     | `scripts/governance/check_runbook_links.py`     | Every runbook link in the indexes and every `runbook:` reference in SLO files resolves to a real file.                                                                       | **Blocking.**                                                                                                   |
| `make verify-traceability`     | aggregate of the three above                    | One command for the full traceability sweep.                                                                                                                                 | —                                                                                                               |

---

## 2. Service Traceability Matrix

Derived from `services.yaml`. ADRs are the full set each service cites in the registry; the SLO
column points at the **canary-gate** file read by `cd-production.yml` (ADR-0073).

| Service            | Type              | Spec                                                                                                                                                                                | Governing ADRs                         | API contract                                                                              | Canary SLO                                                                                       | Runbook(s)                                          | Dashboard                                              | Tests                                       |
| ------------------ | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------- |
| **api-gateway**    | api (python)      | Cross-cutting (`specs/security/rbac-model.md`, `specs/sre/capacity-planning.md`); core request pipeline per CLAUDE.md §0.1                                                          | ADR-0002, 0010, 0011, 0014, 0015       | `docs/api/openapi/v1/openapi.yaml` (REST) · `docs/api/asyncapi/v1/asyncapi.yaml` (events) | `docs/sre/slo/api-gateway.yaml`                                                                  | RB-001, RB-002, RB-006 (`docs/runbooks/`)           | `grafana/dashboards/sre-overview.json`, `agent-*.json` | `tests/` (unit/integration/e2e/abuse_cases) |
| **domain-service** | api (java)        | `specs/features/SPEC-LGS-001-*` (consumer); cross-cutting security specs                                                                                                            | ADR-0002, 0003, 0011                   | `docs/api/asyncapi/v1/asyncapi.yaml` (events)                                             | `docs/sre/slo/domain-service.yaml` ⚠️ `[CONFIRM]`                                                | RB-004 (DB), RB-005 (Kafka)                         | `grafana/dashboards/sre-overview.json`                 | `services/domain-service/`                  |
| **golden-signals** | api (java)        | `specs/system/SPEC-LGS-001-log-based-golden-signals.md`, `specs/features/SPEC-LGS-001-golden-signals-feature-spec.md`, `specs/security/threat-model-SPEC-LGS-001-golden-signals.md` | ADR-0066, 0067, 0068, 0069, 0012, 0026 | REST (ingestion + analytics; no Kafka in initial scope)                                   | `docs/sre/slo/golden-signals.yaml` ⚠️ `[CONFIRM]` (objectives: `golden-signals-objectives.yaml`) | RB-SRE-GS-001, RB-SRE-GS-002 (`docs/sre/runbooks/`) | `grafana/dashboards/golden-signals.json`               | `services/golden-signals/`                  |
| **event-worker**   | worker (go)       | —                                                                                                                                                                                   | ADR-0002, 0003, 0005                   | `docs/api/asyncapi/v1/asyncapi.yaml` (events)                                             | **Exempt** (no inbound request traffic)                                                          | RB-005 (Kafka consumer lag/DLQ)                     | `grafana/dashboards/sre-overview.json`                 | `services/event-worker/`                    |
| **frontend**       | frontend (nodejs) | Cross-cutting (`specs/security/rbac-model.md`)                                                                                                                                      | ADR-0002, 0011                         | Consumes api-gateway REST                                                                 | `docs/sre/slo/frontend.yaml` ⚠️ `[CONFIRM]`                                                      | RB-001 (via api-gateway)                            | —                                                      | `frontend/`                                 |
| **batch-jobs**     | job (python)      | —                                                                                                                                                                                   | ADR-0013, 0011                         | — (CronJob, no inbound port)                                                              | **Exempt** (no inbound request traffic)                                                          | RB-004 (DB)                                         | —                                                      | `tests/` (shared Python suite)              |

> ⚠️ `[CONFIRM]` — the canary thresholds in `domain-service.yaml`, `golden-signals.yaml`, and
> `frontend.yaml` are conservative template defaults and require **SRE-Lead sign-off** (and tuning
> against each service’s own 30d objectives) before that service is promoted to production via
> canary. See [§4](#4-known-gaps).

---

## 3. Topic Traceability

Every topic in `services.yaml` `topics:` must have an Avro schema on disk and a matching AsyncAPI
entry (CLAUDE.md §0.1). Schema presence is **blocking**; AsyncAPI presence is currently **report
mode** because of the naming drift in [§4](#4-known-gaps).

| Topic                      | Producer                | Avro schema                            | In AsyncAPI?                     |
| -------------------------- | ----------------------- | -------------------------------------- | -------------------------------- |
| `request.created.v1`       | api-gateway             | `…/avro/request-created-v1.avsc`       | ⚠️ name drift                    |
| `hitl.decision.v1`         | api-gateway             | `…/avro/hitl-decision-v1.avsc`         | ⚠️ name drift                    |
| `audit.event.v1`           | api-gateway, batch-jobs | `…/avro/audit-event-v1.avsc`           | ⚠️ name drift                    |
| `domain.entity.created.v1` | domain-service          | `…/avro/domain-entity-created-v1.avsc` | ⚠️ name drift                    |
| `domain.entity.updated.v1` | domain-service          | `…/avro/domain-entity-updated-v1.avsc` | ⚠️ name drift                    |
| `event.processed.v1`       | event-worker            | `…/avro/event-processed-v1.avsc`       | ⚠️ name drift                    |
| `domain.request.dlq`       | api-gateway             | `…/avro/domain-request-dlq-v1.avsc`    | (DLQ; not modelled as a channel) |

---

## 4. Known Gaps

Tracked deliberately so the matrix never reads as “fully covered” when it is not. Each gap is either
surfaced as a report-mode warning by a gate, or noted here for a future wave.

1. **AsyncAPI ↔ registry topic-name drift (report mode).** `services.yaml` uses versioned dotted
   names (`request.created.v1`, …); `docs/api/asyncapi/v1/asyncapi.yaml` uses a different scheme
   (`domain.request.created`, `agent.action.proposed`, …). `check_traceability.py` reports this as a
   warning today. **Owner:** Platform team. **Exit:** reconcile the names, then wire
   `STRICT=1`/`--strict` to make it blocking (ADR-0070 burn-in).
2. **`[CONFIRM]` canary SLO thresholds.** `domain-service`, `golden-signals`, and `frontend` carry
   placeholder canary thresholds pending SRE-Lead sign-off. The CD pipeline only deploys
   `api-gateway` today, so these are forward-looking — but they must be tuned before any of those
   services is canary-deployed. **Owner:** SRE Lead.
3. **No dedicated spec for `event-worker` / `batch-jobs`.** Both are governed only by ADRs in the
   registry. If either grows feature surface, author a spec and add it here. **Owner:** Tech Lead.
4. **No dashboard for `frontend`.** Front-end RUM/Golden-Signals dashboard not yet defined.
   **Owner:** SRE Lead.

---

## 5. How to keep this matrix true

- Adding a service to `services.yaml`? Add its row here and (if `type: api`/`frontend`) a
  `docs/sre/slo/<service>.yaml` canary file — `make verify-traceability` will otherwise fail.
- Adding a topic? Add the Avro schema and the AsyncAPI channel in the same change.
- Retiring an artefact? Update the relevant cell to “—” and add a Known Gap entry if the gap is
  intentional.
- CI runs `make verify-traceability`; do not merge with it red (AsyncAPI drift excepted while in
  report mode).
