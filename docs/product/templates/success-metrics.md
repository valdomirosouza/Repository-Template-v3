# Success Metrics — FEAT-{id}: {Feature Name}

> Copy into `docs/product/FEAT-{id}/success-metrics.md` and fill in.
> Add the Agent-Disclosure Header if agent-drafted.
> **Reviewers:** Product Owner + SRE Lead | **Verified at:** Phase 11 (Observability & Operational Readiness)

Defines how we will _observe_ whether the feature delivered value. Every metric must be tied to a
real signal (a Prometheus metric, a log field, a trace, or an SLO) so it is verifiable — not a
slide-deck number. This is the bridge between the value hypothesis and the Golden Signals.

---

## 1. Product metrics (did it deliver value?)

| Metric                 | Definition                             | Baseline | Target  | Source (query / dashboard)    | Owner     |
| ---------------------- | -------------------------------------- | -------- | ------- | ----------------------------- | --------- |
| _Operator review time_ | _median seconds from open to decision_ | _45s_    | _≤ 25s_ | _`hitl_decision_latency` p50_ | _Product_ |

## 2. Adoption / engagement metrics

| Metric             | Definition                        | Target         | Source        |
| ------------------ | --------------------------------- | -------------- | ------------- |
| _Feature adoption_ | _% of eligible sessions using it_ | _≥ 60% in 30d_ | _usage event_ |

## 3. Health / guardrail metrics (must NOT regress)

> Wire these to the Golden Signals (`skills/sre/golden-signals.md`) and, where they gate a release,
> to the service SLO (`docs/sre/slo/<service>.yaml`).

| Signal     | Metric                | Threshold | Alert / SLO link                |
| ---------- | --------------------- | --------- | ------------------------------- |
| Errors     | _wrong-approval rate_ | _< 0.5%_  | _alert: …_                      |
| Latency    | _p99 request latency_ | _≤ SLO_   | _`docs/sre/slo/<service>.yaml`_ |
| Saturation | _HITL queue depth_    | _< N_     | _RB-003_                        |

## 4. AI-specific metrics (if `src/agents/` involved)

| Metric                                   | Why it matters         | Target        |
| ---------------------------------------- | ---------------------- | ------------- |
| _HITL escalation rate_                   | _autonomy calibration_ | _within band_ |
| _Guardrail block rate_                   | _safety signal_        | _monitored_   |
| _Hallucination / unsupported-claim rate_ | _output trust_         | _→ 0_         |

## 5. Review cadence

- **First review:** _date — early signal after launch_
- **Decision review:** _date — judge against `value-hypothesis.md` targets and kill criteria_
- **Owner of the review:** _Product Owner_

## Grounding note

Each "Source" cell must point at a signal that actually exists (or is created by this feature). If a
metric has no source yet, mark it `uncertain — verify` and file the instrumentation work — do not
claim a dashboard that does not exist (CLAUDE.md §3.6, OTEL-001).
