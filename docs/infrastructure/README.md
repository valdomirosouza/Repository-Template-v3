# Infrastructure / IaC Guide

> **Owner:** DevOps Lead + SRE Lead | **Source of truth:** `infrastructure/` (Terraform, Helm, K8s)
> **ADRs:** ADR-0006 (deployment) · ADR-0008 (secrets) · ADR-0029 (DevSecOps) · ADR-0062 (Aurora) · ADR-0063 (brownfield Terraform)

How this system is provisioned and operated as code. This guide documents the **actual** layout and
the standards around it; where a decided control is not yet wired, it is listed as an **owned gap**
(§Conformance) rather than implied to exist.

| Page                                                   | Covers                                                                             |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| [`terraform.md`](terraform.md)                         | Module/env layout, remote state, state bootstrap, drift detection                  |
| [`environment-promotion.md`](environment-promotion.md) | dev → staging → production model (Terraform vars + Helm values + gates)            |
| [`security.md`](security.md)                           | NetworkPolicies, Pod Security, secrets, policy-as-code (Checkov), cost (Infracost) |

---

## 1. Layout (`infrastructure/`)

```
infrastructure/
├── terraform/
│   ├── environments/{dev,staging,production}/main.tf   # one dir per env (no workspaces)
│   └── modules/{networking,database,cache,message-broker,
│                api-gateway,domain-service,event-worker,frontend,observability}
├── helm/{api-gateway,domain-service,event-worker,frontend}/   # values.yaml + values-{dev,staging,production}.yaml
├── k8s/network-policies/   # default-deny + per-service NetworkPolicies
├── feature-flags/          # flagd autonomy flags (ADR-0015)
├── monitoring/             # Prometheus, Grafana, Alertmanager, OTel, Jaeger
└── scripts/{db,deploy}/    # backup/restore, rollback
```

Per ADR-0063, the module names are the canonical roles — **extend modules in place, never fork a
parallel tree**.

## 2. Conformance & gaps

What is actually implemented vs. decided-but-pending. Each gap names an owner; close it in a
dedicated follow-up PR (this guide is docs-only).

| Control                                      | Status                              | Evidence / Owner                                                                                                               |
| -------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Per-env Terraform (dev/staging/prod)         | **Implemented**                     | `terraform/environments/*` call shared modules with per-env vars                                                               |
| Remote state (staging/prod)                  | **Implemented**                     | S3 backend + DynamoDB lock (`encrypt = true`); dev uses local backend by design                                                |
| State bootstrap (bucket + lock table as IaC) | **Implemented**                     | `terraform/bootstrap/` (versioned, encrypted, TLS-only bucket + lock table) — `terraform validate` clean                       |
| Environment promotion model                  | **Implemented**                     | per-env modules + Helm values; ADR-0006, `docs/sre/deployment-strategy.md`                                                     |
| NetworkPolicies (default-deny + per-service) | **Implemented**                     | `k8s/network-policies/` (`default-deny-ingress.yaml`, …)                                                                       |
| Pod Security (`securityContext`)             | **Implemented**                     | all service Helm charts (api-gateway, event-worker, domain-service) + bare manifest hardened                                   |
| Secrets — Vault target                       | **Partial** — decided, not deployed | ADR-0008; today: `detect-secrets` + AWS Secrets Manager for DB creds — DevOps/Security                                         |
| IaC policy-as-code (Checkov)                 | **Report mode** (ADR-0070 burn-in)  | `ci.yml` → _IaC Security Scan (Checkov)_, findings in the CI job summary; SARIF→Security-tab + blocking after burn-in — DevOps |
| Cost estimation in PR (Infracost)            | **Gap**                             | DevOps/FinOps (ADR-0020)                                                                                                       |
| Drift detection (scheduled `terraform plan`) | **Gap**                             | SRE/DevOps                                                                                                                     |

> Recently closed: the api-gateway `securityContext` gap (all service charts now meet the hardened
> baseline), and the **Checkov** IaC scan (ADR-0029) is now wired in **report mode** (ADR-0070
> burn-in), and the TF **state bootstrap** module (`terraform/bootstrap/`). Remaining gaps:
> Infracost, TF drift detection, and the Vault /
> External-Secrets rollout (ADR-0008).
