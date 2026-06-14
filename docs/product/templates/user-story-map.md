# User Story Map — FEAT-{id}: {Feature Name}

> Copy into `docs/product/FEAT-{id}/user-story-map.md` and fill in.
> Add the Agent-Disclosure Header if agent-drafted.
> **Reviewers:** Product Owner + Tech Lead | **Feeds:** `specs/features/FEAT-{id}/feature-spec.md` (§User Stories)

A story map lays the user journey left-to-right (the **backbone** of activities) and slices stories
top-to-bottom by release. It keeps the spec honest: every story here should map to acceptance
criteria and tests.

---

## 1. Backbone — the journey (left → right)

> The sequence of activities the persona moves through to get the job done.

```
[ Activity 1 ]→[ Activity 2 ]→[ Activity 3 ]→[ Activity 4 ]
```

_e.g._ `Sign in → See HITL queue → Inspect a request → Approve / reject → Confirm audit record`

## 2. Stories under each activity

Use the canonical format:

```
As a <persona>,
I want <capability>,
so that <measurable outcome>.
```

| #   | Activity            | Story (As a … I want … so that …)                                                                        | Release slice | Priority |
| --- | ------------------- | -------------------------------------------------------------------------------------------------------- | ------------- | -------- |
| 1   | _Inspect a request_ | _As a HITL Operator, I want to see the agent's reasoning and risk score, so that I can decide in < 30s._ | MVP           | Must     |
| 2   |                     |                                                                                                          |               |          |

> **Release slices:** `MVP` (walking skeleton) → `R2` → `Later`. **Priority:** Must / Should / Could
> (MoSCoW). Everything in the MVP row must be a coherent end-to-end journey, not isolated features.

## 3. Acceptance criteria → test → evidence

For each MVP story, map criteria to how they're verified (mirrors the spec's test strategy and
satisfies the traceability the SDLC expects). Keep AC in Gherkin in the Issue/spec; summarise here:

| Story # | Acceptance criterion (Given/When/Then summary)                             | Test type  | Test file (planned) | Metric/log/trace evidence |
| ------- | -------------------------------------------------------------------------- | ---------- | ------------------- | ------------------------- |
| 1       | _Given a queued request, when opened, then reasoning + risk score render._ | unit + e2e | `tests/e2e/...`     | `hitl_decision_latency`   |

## 4. Out of scope (explicitly)

- _What this feature deliberately does NOT do — prevents scope creep (CLAUDE.md §2 Step 6)._

## 5. Open questions / spikes

- _Unknowns that should become `type: spike` Issues before committing the slice._
