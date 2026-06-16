# Value Hypothesis — FEAT-{id}: {Feature Name}

> Copy into `docs/product/FEAT-{id}/value-hypothesis.md` and fill in.
> Add the Agent-Disclosure Header if agent-drafted. **Reviewer:** Product Owner
> **Seeded at:** Phase 0 (Intake) — the Issue's "Value Hypothesis" line is the one-liner; this is the
> full version.

A falsifiable bet. If you cannot state how you would **disprove** it, it is not a hypothesis.

---

## The hypothesis

> **We believe** that {building this capability}
> **for** {persona / segment}
> **will result in** {measurable outcome}.
> **We will know we are right when** {metric} moves from {baseline} to {target} within {timeframe}.

## Leap-of-faith assumptions

| Assumption                               | Type (desirability / viability / feasibility) | Confidence (L/M/H) | How we de-risk it                   |
| ---------------------------------------- | --------------------------------------------- | ------------------ | ----------------------------------- |
| _Users will trust a bulk-approve action_ | desirability                                  | L                  | _prototype + 5 operator interviews_ |

## Measurement

- **Primary metric:** _the one number that decides success. Link `success-metrics.md`._
- **Baseline (today):** _current value + source (dashboard/query)_
- **Target:** _the value that proves the bet_
- **Guardrail metrics (must NOT regress):** _e.g. wrong-approval rate, p99 latency, error budget_
- **Timeframe / review date:** _when we judge the bet (absolute date)_

## Kill criteria

> If {metric} has not reached {threshold} by {date}, OR a guardrail metric regresses past {limit},
> we will {stop / pivot / re-scope}.

Stating kill criteria up front prevents sunk-cost escalation and keeps autonomy honest.

## Evidence & grounding

_Link the interviews, analytics, or incidents that motivate the bet. Where evidence is missing, mark
`uncertain — verify` (CLAUDE.md §3.6) rather than asserting confidence you don't have._
