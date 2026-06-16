# ADR Review Checklist

> **Owner:** Tech Lead | **Used at:** Phase 5 (Architecture) review, before an ADR is marked `Accepted`.
> Companion to [`ADR-TEMPLATE.md`](ADR-TEMPLATE.md) and the lifecycle in [`README.md`](README.md).

An ADR may move from `Proposed` to `Accepted` only when a reviewer (not the author) can check **all**
applicable boxes. Record the review in the PR that introduces the ADR.

---

## Completeness

- [ ] Uses `ADR-TEMPLATE.md`; no section deleted (N/A noted where it doesn't apply)
- [ ] **Status, Date, Authors, Deciders** filled; status is one of the four lifecycle values
- [ ] **Review-by** date set for `Proposed`/temporary decisions (or `permanent` justified)
- [ ] Added to the **Master Index** in `README.md` with the correct status and date
- [ ] ADR number is the next free integer (no gap, no reuse)

## Decision quality

- [ ] **Context** states the real problem and constraints — not the solution in disguise
- [ ] **Decision** is unambiguous and actionable by an implementer without interpretation
- [ ] **Alternatives** are real options with honest rejection reasons (not strawmen)
- [ ] Consequences include **negative/trade-offs**, not just benefits

## Grounding & non-fabrication (CLAUDE.md §3.6)

- [ ] Every factual/API/version claim is grounded (codebase → specs → Context7 → web) or marked `uncertain — verify`
- [ ] No invented file paths, config keys, ADR numbers, or library behaviours
- [ ] External/library claims cite a source

## Traceability (Wave 1 theme)

- [ ] **Affected services** listed and match `services.yaml` names
- [ ] **Related specs** linked and exist
- [ ] If it supersedes another ADR: old ADR's Status flipped to `Superseded by ADR-NNNN`, and this ADR's `Supersedes` set
- [ ] **Risk mapping** table filled where the decision introduces/addresses risk

## Governance & control surfaces

- [ ] If it touches autonomy / feature flags / guardrails / HITL gateway → governance approval noted (ADR-0015, §14 escalation)
- [ ] If it changes a security/privacy control → Security Lead is a Decider; control matrices updated if needed (ADR-0072)
- [ ] If it changes a runtime SLO/canary contract → SRE Lead is a Decider (ADR-0073)
- [ ] Cost/FinOps impact noted where relevant (ADR-0020)

## Scope discipline

- [ ] One decision per ADR (split if it bundles unrelated decisions)
- [ ] Does not silently contradict an existing Accepted ADR (if it does, it must supersede it explicitly)

---

**Reviewer:** {name — must be someone other than the author} · **Reviewed:** {date} · **Verdict:** Accept / Revise / Reject
