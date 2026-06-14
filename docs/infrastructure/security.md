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

Implemented today in `helm/event-worker`, `helm/domain-service`, and the bare K8s manifest
(`runAsNonRoot`, `readOnlyRootFilesystem`, `capabilities: drop ["ALL"]`).

> **⚠ Owned gap (high priority):** the **api-gateway** Helm template does **not** declare a
> `securityContext` — it should match the baseline above. Track as a Platform follow-up (manifest
> change, out of this docs-only PR).

## 3. Secrets management

- **Target (ADR-0008):** HashiCorp **Vault** as the primary store (cloud secret managers as
  per-env fallback), injected at pod start via the Vault Agent sidecar / CSI driver — the app reads
  env vars or mounted files, **never** Kubernetes `Secret` objects directly.
- **Today:** DB credentials come from **AWS Secrets Manager** (Terraform `module.database` exposes
  `secret_arn`); application secrets are env-injected. `detect-secrets` (+ `.secrets.baseline`) runs
  in `make lint` and pre-commit to block accidental commits.
- **Production guards:** `Settings.reject_placeholder_secrets` blocks deploy if `DB_ENCRYPTION_KEY` /
  `REDIS_TLS_ENABLED` are unset (CLAUDE.md §3.2); Redis is `rediss://` (ADR-0019).
- **Owned gap:** the Vault sidecar / external-secrets (or sealed-secrets) integration is **not yet
  deployed**. Recommended: adopt the External Secrets Operator (`ExternalSecret` CRDs syncing from
  Vault/Secrets Manager) so no plaintext secret is ever committed or stored in a K8s `Secret`.
  **Owner: DevOps/Security.**

## 4. Policy-as-code (IaC scanning)

- **Decided (ADR-0029):** a **Checkov** IaC security scan, blocking on `infrastructure/` changes,
  SARIF to the GitHub Security tab.
- **Reality (owned gap):** Checkov is **not wired** in `ci.yml`, and the existing Trivy _config_ scan
  explicitly **skips `infrastructure/terraform`**. So Terraform is currently unscanned for
  misconfiguration despite the ADR.
- **Recommended:** add Checkov (and `terraform fmt -check`/`validate`) in **report mode** first
  (ADR-0070 burn-in), then flip to blocking once clean. This closes the ADR-0029 ↔ implementation
  drift. **Owner: DevOps.**

## 5. Cost estimation (FinOps)

- **Owned gap:** no per-PR cloud-cost estimation. Recommended: **Infracost** in CI to comment the
  monthly-cost delta of a Terraform change on the PR (ADR-0020 FinOps). **Owner: DevOps/FinOps.**

---

## Summary

Network isolation and most pod hardening are **in place**; the priority gaps are the **api-gateway
`securityContext`** (security baseline not met for that surface) and the **Checkov gate** (decided but
unenforced). Both are manifest/CI changes for dedicated follow-up PRs — this guide records the
standard and the gap so neither is silently assumed done.
