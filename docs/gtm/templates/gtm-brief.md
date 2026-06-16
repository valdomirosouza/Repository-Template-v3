# GTM Brief — {Product / Feature Name}

> Copy into `docs/gtm/FEAT-{id}/gtm-brief.md` (or `docs/gtm/gtm-brief.md` for repo-level).
> Add the Agent-Disclosure Header if agent-drafted. **Reviewer:** Product Owner
> **Status:** Hypothesis — validate before treating any number as committed.

The one-page go-to-market plan. Keep it to a page; depth lives in the linked artefacts.

---

## 1. Ideal Customer Profile (ICP)

- **Firmographics:** _industry, size, region, regulatory context (e.g. LGPD/GDPR-bound)_
- **Trigger / "why now":** _what makes them look for this today_
- **Disqualifiers:** _who this is explicitly NOT for_

## 2. Personas

|           | Persona             | Cares most about           | Link                          |
| --------- | ------------------- | -------------------------- | ----------------------------- |
| **User**  | _who operates it_   | _speed / safety / control_ | `docs/product/.../persona.md` |
| **Buyer** | _who approves/pays_ | _risk / compliance / TCO_  | `docs/product/.../persona.md` |

## 3. Value proposition

> For **{ICP}** who **{need}**, **{product}** is a **{category}** that **{key benefit}**.
> Unlike **{primary alternative}**, we **{key differentiator}**.

## 4. Packaging hypothesis

- **Unit of value:** _what the customer "buys" (seat, service, workflow, environment)_
- **Tiers / editions:** _e.g. OSS template · supported · enterprise-governed_
- **What gates a tier:** _governance features, support SLA, compliance attestations_

## 5. Pricing hypothesis

> ⚠️ Hypothesis — mark assumptions; cite any comparison. Do not invent competitor prices.

- **Model:** _per-seat · usage · platform fee · open-core_
- **Rough anchor:** _value-based reasoning, not a guessed number_
- **Willingness-to-pay signal:** _evidence or `uncertain — verify`_

## 6. Adoption & friction

- **Time-to-first-value target:** _e.g. running + first HITL approval in < 1 hour_
- **Top adoption frictions:** _setup complexity, migration, trust_ → link `adoption-plan.md`

## 7. Launch

- **Launch tier:** _internal · private beta · GA_
- **Success criteria for launch:** _link `success-metrics.md`_
- **Key risks:** _market, execution, compliance_

## 8. Open questions to validate

- [ ] _ICP confirmed with N conversations_
- [ ] _Pricing tested against willingness-to-pay_
- [ ] _Differentiation verified against current alternatives_
