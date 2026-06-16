# Chaos Experiment Catalog

> **Owner:** SRE Lead | **Experiments:** `tests/chaos/experiments/` (Chaos Toolkit) | ADR-0050 (abuse/chaos), ADR-0075 (fallback policy)

The repository ships a suite of **Chaos Toolkit** experiments that inject a single fault and assert a
steady-state hypothesis. This catalog indexes them, records the blast-radius policy, and defines the
GameDay cadence. Each experiment is a real file — run with `chaos run tests/chaos/experiments/<file>`.

---

## 1. Catalog

| Experiment                         | Fault injected              | Steady-state hypothesis (what must hold)                                       |
| ---------------------------------- | --------------------------- | ------------------------------------------------------------------------------ |
| `broker-outage.yaml`               | Kafka scaled to 0 for 90s   | Producers buffer (no drop); all messages delivered on recovery, no offset gaps |
| `network-partition.yaml`           | Partition agent ↔ Kafka     | DLQ catches failures; consumer lag recovers                                    |
| `redis-fallback-activation.yaml`   | Redis outage                | In-memory fallback keeps the service serving (ADR-0075 degrade-open)           |
| `db-audit-fallback-blocked.yaml`   | DB outage in **production** | Audit fallback is **refused** (fail-closed) — no audit loss                    |
| `hitl-store-degradation.yaml`      | HITL store degraded         | Requests queue; **no silent approval**                                         |
| `kill-agent.yaml`                  | Kill agent service          | Golden Signals recover within SLO                                              |
| `llm-api-timeout.yaml`             | LLM API timeout             | Exponential back-off; HITL escalation                                          |
| `evaluator-disagreement.yaml`      | Split evaluator verdict     | HITL escalation on disagreement                                                |
| `agent-context-overflow.yaml`      | Oversized agent context     | Graceful truncation; no crash                                                  |
| `prompt-injection-under-load.yaml` | Injection at concurrency    | Guardrail holds (LLM01)                                                        |

> The catalog mixes **infrastructure** faults (broker/redis/db/network) and **agentic** faults
> (LLM/HITL/guardrail) — both are first-class for an Agentic SDLC platform.

## 2. Blast-radius policy

- **Where:** experiments run against **staging / ephemeral** environments only — never production
  without an approved GameDay plan.
- **Scope:** one fault per experiment; the steady-state hypothesis must reference a **specific** SLO
  or guardrail so a violation is unambiguous.
- **Abort:** every experiment defines rollback (Chaos Toolkit `rollbacks`); abort on any
  steady-state probe failure outside the injected fault.
- **CI:** `chaos-smoke.yml` runs a single-fault resilience smoke on PRs touching worker/HITL/retry
  paths (blocking, deterministic).

## 3. Steady-state hypothesis template

```yaml
steady-state-hypothesis:
  title: "<service> holds <SLO/guardrail> under <fault>"
  probes:
    - name: error-rate-within-slo
      tolerance: { type: range, range: [0, <slo_error_rate>] }
      provider: { type: http, url: "<prometheus>/api/v1/query?query=<sli>" }
```

## 4. GameDay cadence

| Cadence                 | Activity                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------- |
| Per PR (auto)           | `chaos-smoke.yml` single-fault smoke on relevant paths                              |
| Monthly                 | One catalogued experiment in staging; record an experiment report (§5)              |
| Pre-release (high-risk) | Run the experiments relevant to the change (DoR-Release operational gate)           |
| Quarterly GameDay       | Multi-team exercise: pick 2–3 experiments, practice incident response + RB runbooks |

## 5. Experiment report

After each GameDay run, record: experiment, date, environment, hypothesis result (held / violated),
any SLO breach, action items. Store under `docs/resilience/gamedays/<date>-<experiment>.md` (create
the folder when the first report lands). A violated hypothesis is a bug — file an issue.
