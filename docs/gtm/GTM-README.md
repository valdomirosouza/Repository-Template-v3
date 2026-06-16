# Go-to-Market (GTM) Artefacts

> **Owner:** Product Owner (+ Marketing/Sales when present) | **Phase:** 0–2, revisited before release
> **Governance:** Spec-as-PR (`docs/process/HITL-GOVERNANCE.md`) — reviewed via PR, not the runtime HITL gateway

This directory holds the **market-readiness** layer for features (and for the repository itself) that
are meant to become reusable products, not just internal capabilities. It answers _who buys, why us,
how they adopt, and how we talk about it_ — the questions engineering specs deliberately do not.

GTM artefacts are **optional** and apply to **product-facing** features. Internal plumbing, bug
fixes, spikes, and chores do not need them. When in doubt, a feature needs GTM artefacts if an
external user or buyer would notice it.

---

## Templates

| Template                        | Purpose                                                                       | Primary author      |
| ------------------------------- | ----------------------------------------------------------------------------- | ------------------- |
| `templates/gtm-brief.md`        | The one-page GTM plan: ICP, value prop, packaging, pricing hypothesis, launch | Product Owner       |
| `templates/positioning.md`      | Market category, differentiation, competitive alternatives, messaging         | Product / Marketing |
| `templates/adoption-plan.md`    | Onboarding path, time-to-value, adoption friction, success milestones         | Product             |
| `templates/sales-enablement.md` | FAQ, objection handling, qualifying questions, demo script                    | Product / Sales     |

Copy a template into a GTM package for the feature (e.g. `docs/gtm/FEAT-{id}/`) or, for
repository-level positioning, keep a single filled-in copy at `docs/gtm/`.

---

## How GTM connects to discovery

GTM is **downstream of the problem frame, not a replacement for it**. The product discovery
templates (`docs/product/templates/`) establish the problem and the user; GTM establishes the market
and the buyer.

```
problem-framing-canvas.md  → who has the pain, how bad
persona.md (user + buyer)  → who uses vs. who buys
value-hypothesis.md        → the measurable bet
        │
        ▼
gtm-brief.md               → ICP, packaging, pricing hypothesis
positioning.md             → category + differentiation
adoption-plan.md           → onboarding + time-to-value
sales-enablement.md        → how the team sells/explains it
```

---

## Grounding & honesty (CLAUDE.md §3.6)

Pricing, competitive, and market claims are **especially prone to fabrication**. Every competitive
claim, market-size figure, or pricing comparison must cite a source or be marked `uncertain —
verify`. A confidently-stated but unverified market claim is a governance violation, not a
stylistic choice. These are **hypotheses** until validated — name them as such.
