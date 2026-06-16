# Model Lifecycle

> **Owner:** AI Governance Lead | **Registry:** `docs/dependency-manifest.yaml` (`ai_dependencies`) | **Gate:** `tests/model_contract/` (ADR-0051) · `model-card.md`

Every LLM the system depends on moves through an explicit lifecycle. The **registry of record** is
`dependency-manifest.yaml`, which already records each model's `model_id`, `role`, `used_by` paths,
`behavioral_contract_version`, and `last_contract_tested`. This doc defines the **states** and the
**gate** between them.

---

## 1. Lifecycle states

```
Candidate ──contract pass──▶ Approved ──superseded──▶ Deprecated ──removed──▶ Blocked
     │                          │
     └────contract fail─────────┘ (never promoted)
```

| State          | Meaning                                                        | In the manifest                           |
| -------------- | -------------------------------------------------------------- | ----------------------------------------- |
| **Candidate**  | Proposed model/version; not yet in production use              | not listed, or `role: candidate`          |
| **Approved**   | Passed the behavioural contract; bound to `used_by` call sites | listed with `last_contract_tested` recent |
| **Deprecated** | Superseded; still callable but scheduled for removal           | listed; flagged deprecated                |
| **Blocked**    | Must not be used (safety/contract regression)                  | removed from `used_by`; documented        |

## 2. The promotion gate (ADR-0051)

**A new model version MUST NOT be promoted in `dependency-manifest.yaml` without first running
`tests/model_contract/` against it** (CLAUDE.md §3.2). The suite is the behavioural contract:

- `test_pii_non_leakage.py` — no PII leaks in output (LLM06)
- `test_refusal_behavior.py` — refuses out-of-policy requests
- `test_spec_adherence.py` — output conforms to the spec contract

A failure means the candidate stays Candidate. On pass, bump `behavioral_contract_version` and
`last_contract_tested`, and update `used_by`.

## 3. Model upgrade checklist

- [ ] Candidate added; `tests/model_contract/` run against it (ADR-0051) — **all pass**
- [ ] `eval-scorecard.md` re-run — no regression past threshold
- [ ] Prompts targeting the old model re-evaluated (`prompt-registry.md` §3)
- [ ] Cost/latency compared (FinOps, ADR-0020) — token budget impact assessed
- [ ] `model-card.md` updated; `dependency-manifest.yaml` updated (version, dates, used_by)
- [ ] Rollback path recorded (previous Approved version)

## 4. Cost / performance

Each model carries a `role` (e.g. `primary_reasoning`, `low_latency_classification`) — route work to
the cheapest model that meets the contract. Token budget is enforced per environment (ADR-0020);
a model upgrade that blows the budget is a blocking finding.

## 5. Rollback

Reverting to the previous Approved version is always available: restore the prior `model_id`/version
in `dependency-manifest.yaml` at the affected `used_by` sites. Because promotion required a contract
pass, the prior version is known-good by construction.
