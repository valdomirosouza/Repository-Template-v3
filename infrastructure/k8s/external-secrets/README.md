# External Secrets — Reference Manifests

> **ADR:** [ADR-0008 — Secrets Management](../../../docs/adr/ADR-0008-secrets-management.md) ·
> **Guide:** [`docs/infrastructure/security.md`](../../../docs/infrastructure/security.md) §3

These are **reference templates** for the recommended secrets pattern: the
[External Secrets Operator](https://external-secrets.io/) (ESO) syncs values from the source of
record (HashiCorp **Vault** — primary per ADR-0008 — or **AWS Secrets Manager** — fallback) into
Kubernetes `Secret` objects, which the workloads consume. **No secret value is ever committed** —
only the _reference_ to where it lives.

## Files

| File                              | Purpose                                                                         |
| --------------------------------- | ------------------------------------------------------------------------------- |
| `clustersecretstore-vault.yaml`   | `ClusterSecretStore` for Vault (primary, ADR-0008)                              |
| `clustersecretstore-aws.yaml`     | `ClusterSecretStore` for AWS Secrets Manager (fallback)                         |
| `api-gateway-externalsecret.yaml` | `ExternalSecret` → materialises `api-gateway-secrets` (the chart's `secretRef`) |

## How it fits together

```
Vault / AWS Secrets Manager   ──(SecretStore)──▶  ESO  ──(ExternalSecret)──▶  K8s Secret
                                                                              "api-gateway-secrets"
                                                                                      │ envFrom.secretRef
                                                                                      ▼
                                                                            api-gateway pods
```

The api-gateway Helm chart already reads `envFrom: secretRef: api-gateway-secrets`
(`infrastructure/helm/api-gateway/values.yaml`). The `ExternalSecret` here produces exactly that
Secret — so wiring ESO requires **no chart change**.

## Activation (per cluster — not done by these manifests)

These manifests are templates; they require the operator and a configured backend:

```bash
# 1. Install the External Secrets Operator (ESO ≥ 0.10, API external-secrets.io/v1):
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace

# 2. Configure a store (edit the server/role/region), then apply:
kubectl apply -f clustersecretstore-vault.yaml        # or clustersecretstore-aws.yaml
kubectl apply -f api-gateway-externalsecret.yaml      # per namespace/environment
```

## Status (ADR-0008 gap)

This delivers the **reference pattern** (closing "the pattern is undemonstrated"). Operator
deployment + a live Vault/SM backend is a **per-environment** step (a real cluster + secrets store),
so the integration is not "deployed" by this repo. Extend `api-gateway-externalsecret.yaml` `data:`
with every key the app needs (`src/shared/config.py`); replicate the `ExternalSecret` per service.
