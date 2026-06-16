# Product Discovery Templates

> **Owner:** Product Owner | **Phase:** 0–2 (Intake → Conception → Discovery)
> **ADR:** ADR-0052, ADR-0058 | **Governance:** `docs/process/HITL-GOVERNANCE.md`

Reusable templates for the **product conception** layer of the Agentic SDLC. They strengthen the
_why_ and _for whom_ of a feature **before** technical specification, so a spec is never written
against an unframed problem.

Copy a template into the feature's discovery package (`docs/product/FEAT-{id}/`) and fill it in.
`{id}` is the parent GitHub Issue number. These artefacts follow **Spec-as-PR governance** — they are
reviewed via pull request, not the runtime HITL gateway (`docs/process/HITL-GOVERNANCE.md`).

---

## When to use which template

| Template                    | Answers                                                           | Required for                | Reviewer                  |
| --------------------------- | ----------------------------------------------------------------- | --------------------------- | ------------------------- |
| `problem-framing-canvas.md` | What problem, for whom, how painful, what if we do nothing?       | Normal + high-risk features | Product Owner             |
| `persona.md`                | Who is the user / buyer; goals, frustrations, context             | Product-facing features     | Product Owner             |
| `user-story-map.md`         | The user journey decomposed into stories with acceptance criteria | Normal + high-risk features | Product Owner + Tech Lead |
| `value-hypothesis.md`       | The measurable bet and how we'll prove or kill it                 | Normal + high-risk features | Product Owner             |
| `success-metrics.md`        | The metrics/SLIs that tell us it worked, wired to observability   | Product-facing features     | Product Owner + SRE Lead  |

Small bug fixes, spikes, and chores are exempt (see `docs/process/DEFINITION_OF_READY.md` §Exemptions).
Go-to-market artefacts (ICP, positioning, pricing) live in `docs/gtm/` — see `docs/gtm/GTM-README.md`.

---

## Agent-Disclosure Header (mandatory when agent-drafted)

When an agent drafts one of these in a `FEAT-{id}/` package, it **must** carry the disclosure header
(EU AI Act Article 13 transparency; see `docs/product/README.md`):

```markdown
> **⚡ Agent-Generated:** This document was drafted by Claude Code on {date}.
> **Human Review Required:** {role(s)} must review and approve before this artefact is actioned.
> **Review Status:** Draft | Under Review | Approved
> **Reviewer:** {name} | **Approved:** {date}
```

The blank templates here are repository fixtures (not agent-generated), so they omit the header; a
filled-in copy under `FEAT-{id}/` includes it.

---

## How these connect to the rest of the lifecycle

```
Phase 0 Intake        → value-hypothesis.md (seed), risk class on the Issue
Phase 1 Conception    → problem-framing-canvas.md, persona.md  → discovery.md
Phase 2 Discovery     → user-story-map.md, success-metrics.md, nfr.md
Phase 3 Grooming      → DoR checks these exist for product-facing features
Phase 4 Specification → feature-spec.md references the story map + success metrics
Phase 11 Observability→ success-metrics.md SLIs verified against real dashboards/SLOs
```
