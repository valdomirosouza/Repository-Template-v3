# Adoption Plan — {Product / Feature Name}

> Copy into `docs/gtm/.../adoption-plan.md` and fill in. Add the Agent-Disclosure Header if agent-drafted.
> **Reviewer:** Product Owner | **Connects to:** `success-metrics.md` (adoption metrics)

How a new user/team gets from zero to value, and how we remove the friction in between. The north
star is **time-to-first-value (TTFV)**.

---

## 1. Adoption journey

| Stage           | User does                     | Feels                      | Friction to remove   | Our asset                          |
| --------------- | ----------------------------- | -------------------------- | -------------------- | ---------------------------------- |
| **Discover**    | _finds the repo/feature_      | _curious / skeptical_      | _unclear value_      | _README, positioning_              |
| **Evaluate**    | _clones, reads, runs_         | _"will this work for me?"_ | _setup complexity_   | _`make setup-minimal`, quickstart_ |
| **First value** | _completes the golden path_   | _"oh, this is useful"_     | _too many steps_     | _`make smoke`, demo flow_          |
| **Adopt**       | _uses it for real work_       | _confident_                | _migration, trust_   | _docs, examples_                   |
| **Expand**      | _adopts more of the platform_ | _invested_                 | _missing capability_ | _extensions, roadmap_              |

## 2. Time-to-first-value (TTFV)

- **Definition of "first value":** _the concrete moment, e.g. "server running + first HITL approval"_
- **Target TTFV:** _e.g. < 1 hour from clone_
- **Current TTFV:** _measured, or `uncertain — verify`_
- **Golden path:** _the exact happy-path sequence (link the quickstart)_

## 3. Onboarding path

```
clone → make setup-minimal → make run → make smoke → <first-value action> → <next step>
```

_List the actual commands/links. If a step does not yet exist, mark it as a gap, don't imply it works._

## 4. Adoption friction log

| Friction                              | Severity | Mitigation              | Owner     |
| ------------------------------------- | -------- | ----------------------- | --------- |
| _e.g. requires Docker for full stack_ | M        | _document minimal tier_ | _Product_ |

## 5. Success milestones

| Milestone   | Signal                  | Target    | Source                 |
| ----------- | ----------------------- | --------- | ---------------------- |
| _Activated_ | _completed golden path_ | _N teams_ | _`success-metrics.md`_ |
| _Retained_  | _used again in 7d_      | _X%_      |                        |

## 6. Adoption risks

- _What could stall adoption (trust, learning curve, integration), and the plan to address it._
