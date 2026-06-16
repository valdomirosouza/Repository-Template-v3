# Environment Promotion — dev → staging → production

> **Owner:** SRE Lead + DevOps Lead | ADR-0006 (deployment) · `docs/sre/deployment-strategy.md`

The same code and the same Terraform modules / Helm charts flow through three environments; only the
**parameters** change. Promotion is forward-only and change-managed for staging→production.

## 1. The model

```
code merged to main
   │
   ▼  build + sign image (cosign), SBOM
dev ──────────► staging ──────────► production
 local TF state   S3 TF state          S3 TF state
 1 AZ, 1 node     2 AZ, 2-5 nodes      3 AZ, 3-20 nodes
 replicas: 1      replicas: 1          replicas: 3 (PDB minAvailable 2)
                  smoke + DAST gate     CAB + canary 5%→25%→100% + SLO gate
```

## 2. What differs per environment (verified)

**Terraform** (`environments/<env>/main.tf` — same modules, different vars):

| Dimension                    | dev           | staging       | production    |
| ---------------------------- | ------------- | ------------- | ------------- |
| VPC CIDR                     | `10.2.0.0/16` | `10.1.0.0/16` | `10.0.0.0/16` |
| Availability zones           | 1             | 2             | 3             |
| Node instance type           | `t3.medium`   | `m6i.large`   | `m6i.xlarge`  |
| Node count (desired/min/max) | 1 / 1 / 2     | 2 / 1 / 5     | 3 / 3 / 20    |
| TF backend                   | local         | S3 + DynamoDB | S3 + DynamoDB |

**Helm** (`helm/<svc>/values-<env>.yaml` overlay `values.yaml`): replica count, CPU/memory
requests/limits, and PodDisruptionBudget scale up dev → prod (e.g. api-gateway `replicaCount` 1 → 1 →
3; `pdb.minAvailable` 0 → … → 2). Image tag/digest is set by the deploy pipeline, not committed.

## 3. Promotion gates

| Transition           | Gate                                                                                                                                                                               |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| main → dev           | CI green; auto-deployable                                                                                                                                                          |
| dev → staging        | image built, signed, SBOM attested; staging smoke + **DAST (ZAP)** must pass                                                                                                       |
| staging → production | **CAB approval** (ISO 27001, ADR-0027) + canary 5%→25%→100% with the per-service SLO gate (`docs/sre/slo/<service>.yaml`, ADR-0073) + error-budget check; auto-rollback on failure |

The production canary thresholds come from the per-service SLO file (ADR-0073) — see
`docs/governance/traceability-matrix.md` for which services have one.

## 4. Rules

- **Never skip an environment** — production only receives images that passed staging.
- **Parameters, not forks** — a new env is a new `environments/<env>/` dir reusing the modules; new
  per-env behaviour is a Helm `values-<env>.yaml` override, not a template change.
- **Promotion is forward-only**; recovery is rollback (`make rollback`, RB-001), not a reverse promote.
