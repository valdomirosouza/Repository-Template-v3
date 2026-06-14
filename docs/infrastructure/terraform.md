# Terraform — Layout, Remote State, Drift

> **Owner:** DevOps Lead | **Source of truth:** `infrastructure/terraform/` | ADR-0063 (brownfield reconciliation), ADR-0062 (Aurora)

## 1. Structure

One **directory per environment** (no Terraform workspaces) calling a shared set of modules:

```
terraform/
├── environments/{dev,staging,production}/main.tf
└── modules/{networking,database,cache,message-broker,
             api-gateway,domain-service,event-worker,frontend,observability}
```

Each `environments/*/main.tf` pins `required_version` and `required_providers` and instantiates the
same modules with environment-specific variables (see [`environment-promotion.md`](environment-promotion.md)).
Extend modules **in place** — never fork a parallel tree (ADR-0063).

## 2. Remote state

| Env        | Backend           | Notes                                                                                |
| ---------- | ----------------- | ------------------------------------------------------------------------------------ |
| dev        | `backend "local"` | intentional — no state bucket needed; `terraform.tfstate` is git-ignored             |
| staging    | `backend "s3"`    | `encrypt = true`, `dynamodb_table` lock; key `monorepo/staging/terraform.tfstate`    |
| production | `backend "s3"`    | `encrypt = true`, `dynamodb_table` lock; key `monorepo/production/terraform.tfstate` |

The S3 bucket name (`your-org-terraform-state`) is a **template placeholder** — substitute it at
adoption (`make template-init` / `docs/governance/owner-onboarding.md`). State is encrypted at rest
and locked via DynamoDB to prevent concurrent applies.

### State bootstrap

The state bucket and DynamoDB lock table are provisioned by a one-time, local-backend module:
[`infrastructure/terraform/bootstrap/`](../../infrastructure/terraform/bootstrap/README.md). It
creates a **versioned, encrypted, public-access-blocked, TLS-only** S3 state bucket and a
`PAY_PER_REQUEST` DynamoDB lock table (with point-in-time recovery), then you point each
environment's `backend "s3"` block at its outputs (`terraform output backend_config_hint`). Run it
once per AWS account before the first environment `apply`.

## 3. Workflow

```bash
cd infrastructure/terraform/environments/<env>
terraform init      # configures the backend
terraform plan      # review BEFORE apply — never apply an unreviewed plan
terraform apply     # staging/production applies are change-managed (ADR-0027, CAB)
```

Production applies follow ISO 27001 change management (CLAUDE.md §11) — a reviewed plan attached to
the RFC, applied in a change window.

## 4. Drift detection (owned gap)

There is no scheduled drift check today. Recommended: a scheduled workflow (e.g. nightly) running
`terraform plan -detailed-exitcode` per environment and alerting on a non-zero (drift) exit, so
out-of-band console changes are caught. Pair with ADR-0063's reconciliation discipline
(`terraform state mv`, import) rather than re-creating drifted resources. **Owner: SRE/DevOps.**

## 5. Validation in CI (owned gap)

`terraform fmt -check` / `terraform validate` and an IaC policy scan (Checkov, ADR-0029) are **not
yet wired** — see [`security.md`](security.md) §Policy-as-code. Recommended order: add `fmt`/`validate`
(fast, deterministic) first, then Checkov in report mode (ADR-0070 burn-in) before blocking.
