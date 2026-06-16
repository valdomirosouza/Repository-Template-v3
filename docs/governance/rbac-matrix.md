# RBAC Matrix — Roles, Access & Authority

> **Owner:** Security Lead + Tech Lead | **Related:** [`raci-matrix.md`](raci-matrix.md) · [`.github/CODEOWNERS`](../../.github/CODEOWNERS) · ADR-0011 (HITL/HOTL) · ADR-0015 (autonomy flags) · ADR-0027 (CAB)

Who can do what, across three planes: **GitHub** (repo/PR), **Runtime** (the deployed system, incl.
agent autonomy), and **Approval authority** (which gates a role can sign off). This complements the
RACI (which maps roles to _process steps_); here the focus is _enforced permissions_.

The **runtime** plane for agents is the autonomy ladder (ADR-0015, `src/shared/feature_flags.py`):
`NONE → READ_ONLY → TESTS_ONLY → LOW_RISK → MEDIUM_RISK → FULL`, default `NONE`. Personas
(`.claude/personas/`) cap a session's ceiling; raising past `LOW_RISK` needs ADR-0015 sign-off.

---

## Human roles

| Role                              | GitHub permission                                                                                             | Runtime permission                                     | Approval authority                                          | Notes                                                  |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------- | ------------------------------------------------------ |
| **Tech Lead** (TL)                | Maintain; CODEOWNER for `docs/adr/`, `specs/`, `CLAUDE.md`                                                    | Admin (break-glass, audited)                           | ADRs; CAB (normal/emergency); DoR/DoD                       | Owns architecture + change board                       |
| **Product Owner** (PO)            | Write; CODEOWNER for `specs/`                                                                                 | Read (dashboards)                                      | Discovery viability; acceptance criteria                    | No infra/secrets access                                |
| **Developer / Engineering** (ENG) | Write; PR author                                                                                              | Read + deploy to **dev** via CI                        | Code review (non-self for financial paths, SOX)             | Cannot self-approve own PR on `src/*`                  |
| **Security Lead** (SEC)           | Maintain; CODEOWNER for `src/guardrails/`, `.github/workflows/`, security specs                               | Read; secret-rotation; guardrail config                | Threat model; security gates; HITL gateway (dual)           | Dual-approval on `hitl_gateway.py`                     |
| **Data Protection Officer** (DPO) | Write; CODEOWNER for `docs/privacy/`                                                                          | Read (audit/PII inventory)                             | DPIA/RIPD; data-subject-rights                              | LGPD/GDPR sign-off                                     |
| **AI Governance Lead** (AIGOV)    | Maintain; CODEOWNER for `src/shared/feature_flags.py`, `infrastructure/feature-flags/`, `docs/ai-governance/` | Sets autonomy flags; reviews agent audit log           | Autonomy changes (ADR-0015); model/prompt promotion         | Sole owner of HOTL enablement                          |
| **SRE Lead** (SRE)                | Maintain; CODEOWNER for `docs/sre/`, runbooks                                                                 | Prod observability; canary/rollback                    | PRR; SLO sign-off; per-service canary thresholds (ADR-0073) | Incident commander pool                                |
| **DevOps Lead** (DEV)             | Maintain; CODEOWNER for `.github/workflows/`, `infrastructure/`                                               | Prod deploy execution; Terraform apply                 | Pipeline/IaC changes                                        | Holds prod OIDC role                                   |
| **Release Manager**               | Write                                                                                                         | Triggers `cd-production.yml`                           | RC approval (`rc-approved`); production promotion           | May be the TL/DEV by rotation                          |
| **HITL Operator**                 | n/a (runtime user)                                                                                            | JWT role `hitl-operator`: approve/reject HITL requests | Per-request HITL decisions (≤ threshold)                    | Identity from JWT `sub`, never request body (REM-001)  |
| **HOTL Supervisor**               | n/a (runtime user)                                                                                            | Monitor autonomous actions; **override + kill-switch** | Production autonomy review cadence                          | Activated only when `autonomous-mode` is on (ADR-0015) |

## Non-human principal

| Principal               | GitHub permission   | Runtime permission                                                                    | Approval authority                                | Notes                                                                              |
| ----------------------- | ------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **AI Agent** (delivery) | Opens PRs, comments | None — **stops at every human gate**                                                  | **None** — recommends/prepares only               | Never autonomously merges, deploys, releases, or changes autonomy flags (ADR-0058) |
| **AI Agent** (runtime)  | n/a                 | Bounded by the autonomy level; all real-world actions route through `hitl_gateway.py` | None — actions gated by HITL/HOTL + feature flags | Permissions never exceed `specs/ai/guardrails.md`                                  |

---

## Enforcement points

- **GitHub permissions** → branch protection (ADR-0071) + `.github/CODEOWNERS` (≥ 2 approvers on
  `src/*`/`services/*`/`infrastructure/*`; SoD for financial paths, SOX §10).
- **Runtime/agent autonomy** → OpenFeature/flagd flags (`src/shared/feature_flags.py`), HITL gateway,
  and the high-risk-action guard hook (issue #133).
- **Approval authority** → CAB gate (`cd-production.yml` `cab-check`), governance-council/legal labels
  (`governance-gate.yml`), and the Spec-as-PR review gates.

> Substitute the placeholder GitHub handles (`@your-org/...`) at adoption — see
> `docs/governance/owner-onboarding.md`. Any change to an agent's runtime authority is an ADR-0015
> `normal-change` requiring AI Governance + governance-council sign-off.
