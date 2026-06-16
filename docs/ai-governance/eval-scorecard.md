# Evaluation Scorecard

> **Owner:** AI Governance Lead | **Implements against:** `src/agents/harness/evaluator.py` · `tests/model_contract/` | ADR-0051

How agent/LLM output quality and safety are **measured**, so a prompt or model change can be judged
objectively (not vibes). The runtime evaluator (`harness/evaluator.py`, LLM-as-judge) already scores
generator output on multiple dimensions and audit-logs every score; this scorecard standardises the
offline eval that gates changes.

---

## 1. Eval dataset format

A versioned set of cases, each: `id`, `input`, `context`, `expected` (or a rubric), `tags`, and the
`risk_class`. Store per capability (e.g. `evals/planner/`, `evals/evaluator/`). Cases must include
**adversarial** items (injection, PII bait) and **edge** items, not just happy paths.

## 2. Quality metrics (from the evaluator dimensions)

The runtime `EvaluatorScore` records dimension scores per output; the offline scorecard aggregates the
same dimensions over the dataset:

| Metric                   | Definition                                                  | Target     |
| ------------------------ | ----------------------------------------------------------- | ---------- |
| Correctness              | output meets the spec/expected                              | ≥ baseline |
| Completeness             | covers all required elements                                | ≥ baseline |
| Faithfulness / grounding | claims supported by provided context (no fabrication, §3.6) | ↑, → 1.0   |
| Format adherence         | conforms to the required output contract                    | ≥ baseline |

## 3. Safety metrics

| Metric                                 | Source                                                  | Target |
| -------------------------------------- | ------------------------------------------------------- | ------ |
| PII leakage rate                       | `tests/model_contract/test_pii_non_leakage.py`          | 0      |
| Refusal correctness                    | `test_refusal_behavior.py`                              | passes |
| Guardrail block rate (injection)       | `prompt_injection_guard.py` + abuse cases (ADR-0050)    | holds  |
| Hallucination / unsupported-claim rate | grounding check (`hallucination-detection` — see below) | → 0    |

## 4. Regression thresholds

- A prompt/model change **must not** drop any quality dimension below its recorded baseline, and
  **must not** regress any safety metric at all (safety is a hard gate).
- Wire the scorecard into the model-contract gate (`model-lifecycle.md` §2): a regression blocks
  promotion.

## 5. Human review

- **Sample rate:** review a fixed % of low-confidence / high-risk outputs (risk score ≥ 0.7 routes to
  HITL anyway — LLM09).
- **Leaderboard:** keep a comparison of prompt/model variants over the dataset (which version scores
  best per dimension) to inform promotion decisions.

## 6. Hallucination detection

Factuality is a first-class metric: every claim must be grounded in provided context or marked
`uncertain — verify` (CLAUDE.md §3.6). Low-confidence / unsupported outputs route to human review.
Track the unsupported-claim rate as a release-over-release trend.
