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

### State bootstrap (owned gap)

The state bucket and DynamoDB lock table are currently assumed **pre-created out of band** — there is
no bootstrap module. Recommended: a tiny one-time `terraform/bootstrap/` (local backend) that
provisions the versioned, encrypted S3 bucket + lock table, then migrate. Until it exists, document
the manual creation steps in the org runbook. **Owner: DevOps.**

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
