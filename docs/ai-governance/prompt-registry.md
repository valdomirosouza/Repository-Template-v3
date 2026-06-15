# Prompt Registry

> **Owner:** AI Governance Lead | **Related:** [`model-lifecycle.md`](model-lifecycle.md) · [`eval-scorecard.md`](eval-scorecard.md) · `docs/dependency-manifest.yaml` · ADR-0051 (model contracts)

A prompt is production code: a change to it changes model behaviour as surely as a code change. This
registry makes every system/instruction prompt **owned, versioned, purposeful, and evaluated** —
never an untracked string edit.

---

## 1. Where prompts live today

Prompts are currently **inline** in the harness/orchestrator (no separate `prompts/` tree yet):

| Prompt                               | Location                                   | Purpose                                  |
| ------------------------------------ | ------------------------------------------ | ---------------------------------------- |
| Planner                              | `src/agents/harness/planner.py`            | Decompose a spec into a sprint/task plan |
| Evaluator (LLM-as-judge)             | `src/agents/harness/evaluator.py`          | Score generator output on 4 dimensions   |
| Orchestrator (Perception→Reason→Act) | `src/agents/orchestrator/orchestrator.py`  | Drive the agent loop                     |
| Sub-agent registry                   | `src/agents/harness/sub_agent_registry.py` | Specialised sub-agent instructions       |
| Spec-contract enforcer               | `src/agents/spec_contract_enforcer.py`     | Hold output to the spec contract         |

> **Recommended evolution:** extract prompts into a versioned `prompts/` tree (one file per prompt,
> with the metadata below) so diffs are reviewable in isolation. Until then, the discipline in §2
> applies to the inline prompts.

## 2. Required metadata per prompt

| Field                  | Why                                                                      |
| ---------------------- | ------------------------------------------------------------------------ |
| **Owner**              | Accountable role (AI Governance / Tech Lead)                             |
| **Purpose**            | The single job this prompt does                                          |
| **Version**            | SemVer; bump on any wording change that can alter behaviour              |
| **Model version(s)**   | Which model(s) it is written/tuned for — link `dependency-manifest.yaml` |
| **Evaluation dataset** | The eval set that validates this prompt (`eval-scorecard.md`)            |
| **Rollback**           | The previous known-good version to revert to                             |

## 3. Change discipline

- A prompt change is a **behavioural change** → it must pass the model-contract suite
  (`tests/model_contract/`, ADR-0051) and not reduce the eval scorecard (`eval-scorecard.md`).
- **Prompt version ↔ model version are coupled:** record which model a prompt targets; re-evaluate a
  prompt when its model is upgraded (`model-lifecycle.md`).
- The **prompt-injection guard** (`src/guardrails/prompt_injection_guard.py`) is never disabled and is
  not part of the editable prompt — it wraps every model call (LLM01).
- Never embed secrets or real PII in a prompt; PII is masked by `pii_filter.py` before any model call
  (LLM06).
