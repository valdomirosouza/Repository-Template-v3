<!--
  OPTIONAL spec addendum — copy the sections you need into your feature spec (after §15 Open
  Questions, before §16 References), or keep as a sibling file linked from §16.

  Why an addendum (not new mandatory sections in SPEC-TEMPLATE.md): the template's numbered sections
  are a contract that /deliver and docs/process/gates/phase-gates.yaml depend on, so the core stays
  stable. These sections are CONDITIONAL — fill them only when the trigger applies. They strengthen
  product-facing, high-risk, and AI features without burdening every small spec.
-->

# Spec Addendum — Product & Operational Readiness

> Conditional companion to `specs/SPEC-TEMPLATE.md`. Each section lists its **trigger**; omit (or write
> "N/A — <reason>") when the trigger does not apply.

---

## A. Product hypothesis _(trigger: product-facing feature)_

The measurable bet behind this feature. Link the discovery artefacts rather than duplicating them:

- **Value hypothesis:** `docs/product/FEAT-{id}/value-hypothesis.md`
- **Primary success metric + target + kill criteria:** summarise here; full detail in
  `docs/product/FEAT-{id}/success-metrics.md`
- **Persona(s):** `docs/product/FEAT-{id}/persona.md` (user; buyer if distinct)

> Keeps the spec honest about _why_ — a spec with no measurable value hypothesis is a solution
> looking for a problem.

## B. GTM relevance _(trigger: feature positioned as a reusable/sellable capability)_

- **Is this externally visible / part of the product's value prop?** yes / no
- **GTM brief:** `docs/gtm/.../gtm-brief.md` (ICP, packaging, pricing hypothesis) — link if it exists
- **Positioning impact:** does this change the category/differentiation story? (`docs/gtm/.../positioning.md`)

If "no" to all, write "N/A — internal capability."

## C. Rollout & backout strategy _(trigger: any runtime change)_

- **Rollout:** flag-gated? canary (per `docs/sre/slo/<service>.yaml`)? phased by tenant?
- **Backout:** how to disable/roll back fast (feature flag off, `make rollback`, RB-001). State the
  **rollback time objective** and whether rollback was tested in staging (ISO 27001 CM, ADR-0027).
- **Data/migration reversibility:** are schema/data changes backward-compatible? expand→migrate→contract?

## D. Operational failure modes _(trigger: any runtime surface)_

Enumerate how this fails in production and the response. Each row should map to a Golden Signal and,
where applicable, an alert + runbook.

| Failure mode                       | Detection (signal/alert) | Blast radius      | Mitigation / runbook           |
| ---------------------------------- | ------------------------ | ----------------- | ------------------------------ |
| _dependency (Redis/Kafka/DB) down_ | _alert_                  | _degraded / down_ | _fallback (ADR-0075) / RB-NNN_ |
| _capacity exhausted_               | _saturation_             | _503s_            | _scale / shed load_            |

Cross-check the fallback posture against ADR-0075 (degrade-open vs fail-closed).

## E. AI evaluation strategy _(trigger: `src/agents/`, `src/guardrails/`, a new `action_type`, prompt, model, or autonomy change)_

> If this triggers, Phase 10 (AI Safety) is mandatory (CLAUDE.md §2; ADR-0058).

- **Eval dataset:** what scenarios validate behaviour; where the dataset lives
- **Quality + safety metrics:** factuality/grounding, guardrail block rate, HITL escalation/rejection
  rate, hallucination/unsupported-claim rate (tie to `success-metrics.md` §4)
- **Regression thresholds:** what score drop blocks promotion (`tests/model_contract/`, ADR-0051)
- **Prompt/model versioning:** prompt + model version this spec assumes; rollback path
- **Abuse cases:** new/changed entries in `tests/abuse_cases/` (ADR-0050 — never reduce the count)
- **Human-review threshold:** risk score ≥ 0.7 routes to HITL (LLM09); confirm or justify deviation

---

> **Grounding (CLAUDE.md §3.6):** every metric source, dataset, alert, and runbook referenced here
> must exist or be marked `uncertain — verify`. Do not cite a dashboard, dataset, or runbook that has
> not been created.
