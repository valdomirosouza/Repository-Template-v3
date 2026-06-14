# Infrastructure Security — Network, Pod, Secrets, Policy-as-Code

> **Owner:** Security Lead + DevOps Lead | ADR-0008 (secrets) · ADR-0029 (DevSecOps) · CLAUDE.md §3.2

## 1. Network policies

Pod-to-pod traffic is **default-deny** with explicit allow-lists (`infrastructure/k8s/network-policies/`):

| File                        | Role                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------ |
| `default-deny-ingress.yaml` | `podSelector: {}` + `policyTypes: [Ingress]`, no rules → deny all inbound by default |
| `api-gateway.yaml`          | explicit ingress/egress for the gateway (namespace-scoped, port 8000)                |
| `monitoring.yaml`           | allows the Prometheus scrape path                                                    |
| `istio-peer-auth.yaml`      | mTLS peer authentication (service mesh)                                              |
| `README.md`                 | how the policies compose                                                             |

**Standard:** every new service ships its own NetworkPolicy with the **minimum** ingress/egress it
needs; nothing relies on the absence of a policy. Egress to the internet follows the SSRF allow-list
posture (OWASP A10, `scripts/governance/check_outbound_urls.py`).

## 2. Pod Security (`securityContext`)

**Standard** (hardened baseline, ≈ PSS _restricted_) for every workload:

```yaml
securityContext: # pod
  runAsNonRoot: true
  runAsUser: <non-zero>
  fsGroup: <non-zero>
  seccompProfile: { type: RuntimeDefault }
containers:
  - securityContext: # container
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities: { drop: ["ALL"] }
```

Implemented in **all** service Helm charts — `helm/api-gateway`, `helm/event-worker`,
`helm/domain-service` — and the bare K8s manifest: pod-level `runAsNonRoot`/`runAsUser`/`fsGroup` and
container-level `allowPrivilegeEscalation: false`/`readOnlyRootFilesystem: true` (the bare manifest
additionally drops all capabilities).

## 3. Secrets management

- **Target (ADR-0008):** HashiCorp **Vault** as the primary store (cloud secret managers as
  per-env fallback), injected at pod start via the Vault Agent sidecar / CSI driver — the app reads
  env vars or mounted files, **never** Kubernetes `Secret` objects directly.
- **Today:** DB credentials come from **AWS Secrets Manager** (Terraform `module.database` exposes
  `secret_arn`); application secrets are env-injected. `detect-secrets` (+ `.secrets.baseline`) runs
  in `make lint` and pre-commit to block accidental commits.
- **Production guards:** `Settings.reject_placeholder_secrets` blocks deploy if `DB_ENCRYPTION_KEY` /
  `REDIS_TLS_ENABLED` are unset (CLAUDE.md §3.2); Redis is `rediss://` (ADR-0019).
- **Reference pattern (provided):** External Secrets Operator manifests live in
  [`infrastructure/k8s/external-secrets/`](../../infrastructure/k8s/external-secrets/README.md) — a
  Vault (primary) and an AWS Secrets Manager (fallback) `ClusterSecretStore`, plus an `ExternalSecret`
  that materialises `api-gateway-secrets` (the chart's `secretRef`) so no plaintext secret is ever
  committed or hand-created. **Partial:** these are templates — operator install + a live
  Vault/Secrets-Manager backend is a per-environment step (real cluster + store). **Owner:
  DevOps/Security.**

## 4. Policy-as-code (IaC scanning)

- **Decided (ADR-0029):** a **Checkov** IaC security scan, blocking on `infrastructure/` changes,
  SARIF to the GitHub Security tab.
- **Reality:** Checkov is now wired as the `iac-scan` job in `ci.yml`, scanning `infrastructure/`
  (terraform + Helm + K8s) — closing the ADR-0029 ↔ implementation drift. It complements the Trivy
  config scan (which covers Helm/K8s but skips `infrastructure/terraform`).
- **Mode:** **report mode** (`continue-on-error`, ADR-0070 burn-in) — findings are written to the CI
  **job summary** (advisory) and do not block. SARIF is intentionally **not** uploaded in report
  mode (a code-scanning SARIF upload creates a separate failing "Checkov" check whenever findings
  exist, defeating report mode). When the gate flips to blocking — after the burn-in in
  `docs/governance/gate-lifecycle.md` is met (HITL-approved `normal-change`) — restore the SARIF
  upload to the Security tab and drop `continue-on-error`. **Owner: DevOps.**

## 5. Cost estimation (FinOps)

- **Owned gap:** no per-PR cloud-cost estimation. Recommended: **Infracost** in CI to comment the
  monthly-cost delta of a Terraform change on the PR (ADR-0020 FinOps). **Owner: DevOps/FinOps.**

---

## Summary

Network isolation and pod hardening are **in place across all service charts**. The remaining
priority gap is the **Checkov gate** (decided in ADR-0029 but unenforced — Trivy config scan skips
`infrastructure/terraform`); secrets-via-Vault/External-Secrets and Infracost are also tracked gaps.
This guide records the standard and each gap so none is silently assumed done.
