# Problem Framing Canvas — FEAT-{id}: {Feature Name}

> Copy into `docs/product/FEAT-{id}/problem-framing-canvas.md` and fill in.
> Add the Agent-Disclosure Header (see `docs/product/templates/README.md`) if agent-drafted.
> **Reviewer:** Product Owner | **Gate:** informs `discovery.md` (Phase 1)

A one-page frame of the problem **before** any solution is proposed. If a row cannot be answered with
evidence, that is itself a finding — note it and consider a spike (`type: spike` Issue).

---

| Field                           | Your answer                                                                            |
| ------------------------------- | -------------------------------------------------------------------------------------- |
| **Customer segment**            | _Which market/customer group? e.g. enterprise SRE teams, regulated fintechs_           |
| **User persona**                | _Who performs the task? Link `persona.md`. e.g. HITL Operator_                         |
| **Buyer persona**               | _Who decides to adopt/pay? (may differ from the user) e.g. Head of Platform_           |
| **Problem statement**           | _One sentence, in the user's words. "When I … I can't … because …"_                    |
| **Current workaround**          | _What do they do today without this? (spreadsheets, manual steps, a competitor)_       |
| **Pain intensity**              | _How often + how much it hurts. Frequency × severity. e.g. daily, blocks releases_     |
| **Business impact**             | _Cost of the pain: time, money, risk, churn, compliance exposure_                      |
| **Risk of doing nothing**       | _What happens if we don't build this? (status-quo cost, escalating risk)_              |
| **Expected measurable outcome** | _The change we expect, as a number. Link `value-hypothesis.md` + `success-metrics.md`_ |
| **Evidence source**             | _Where this is grounded: ticket #, interview, metric, incident, support volume_        |

---

## Anti-patterns (reject the frame if any are true)

- [ ] The "problem" is actually a pre-chosen solution in disguise.
- [ ] No evidence source — the pain is assumed, not observed.
- [ ] The measurable outcome is a vanity metric (activity, not value).
- [ ] User persona and buyer persona are conflated when they differ.

## Grounding note (CLAUDE.md §3.6)

Every claim in this canvas must be grounded (codebase → specs/docs → Context7 → web → "uncertain —
verify"). Do not fabricate evidence. If the evidence source column would be empty, write
`uncertain — verify` rather than inventing a justification.
