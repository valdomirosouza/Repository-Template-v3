# Terraform State Backend Bootstrap

> **Owner:** DevOps Lead | One-time, per AWS account. Companion: [`docs/infrastructure/terraform.md`](../../../../docs/infrastructure/terraform.md)

The `staging`/`production` environments use an **S3 backend + DynamoDB lock table** for remote state.
Those resources can't be created by the config that uses them as a backend (chicken-and-egg), so this
module provisions them with a **local backend**. Run it once before the first environment `apply`.

## Usage

```bash
# 1. (Optional) override the placeholder bucket name — it must be globally unique.
export TF_VAR_state_bucket_name="myorg-terraform-state"

cd infrastructure/terraform/bootstrap
terraform init
terraform apply        # creates the versioned, encrypted, TLS-only state bucket + lock table

# 2. Wire the environments to the outputs (terraform output backend_config_hint):
#    edit environments/<env>/main.tf  →  backend "s3" { bucket=…, dynamodb_table=…, region=… }
#    then:  terraform -chdir=infrastructure/terraform/environments/<env> init -migrate-state
```

## What it creates

| Resource            | Hardening                                                                                                                     |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| S3 state bucket     | versioning **on**, encryption at rest (SSE-S3 or KMS via `kms_key_arn`), public access **blocked**, non-TLS access **denied** |
| DynamoDB lock table | `LockID` hash key, `PAY_PER_REQUEST`, point-in-time recovery                                                                  |

## State of this module

This module's own state is **local** (`terraform.tfstate`, git-ignored). Keep it somewhere safe, or
migrate it into the bucket it creates. Inputs (`variables.tf`): `aws_region`, `state_bucket_name`,
`lock_table_name`, `kms_key_arn`, `tags`. Validated with `terraform validate` + `terraform fmt`.
