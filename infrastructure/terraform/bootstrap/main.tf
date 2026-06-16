# Terraform state backend bootstrap (run ONCE per AWS account, before any environment apply).
#
# The environment configs (environments/{staging,production}) use an S3 backend with a DynamoDB
# lock table. Those resources cannot be created by the same config that uses them as a backend
# (chicken-and-egg), so this module provisions them with a LOCAL backend. After applying, point the
# environments' `backend "s3"` block at the outputs below.
#
# Apply:  terraform -chdir=infrastructure/terraform/bootstrap init
#         terraform -chdir=infrastructure/terraform/bootstrap apply
# ADR:    ADR-0006 (Deployment Strategy), ADR-0063 (Brownfield Terraform reconciliation)

terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Local backend on purpose: this is the module that CREATES the remote-state backend, so it cannot
  # use it. Commit the resulting terraform.tfstate to a secure location (it is git-ignored), or
  # migrate it into the bucket it creates after the first apply.
  backend "local" {}
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = merge({
      ManagedBy = "terraform"
      Component = "tf-state-bootstrap"
    }, var.tags)
  }
}

# ── State bucket ────────────────────────────────────────────────────────────────
resource "aws_s3_bucket" "state" {
  bucket = var.state_bucket_name
}

# Versioning lets you recover a previous state if an apply corrupts it.
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Encrypt state at rest (it can contain secrets/outputs). aws:kms when a key is supplied, else SSE-S3.
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_arn == "" ? "AES256" : "aws:kms"
      kms_master_key_id = var.kms_key_arn == "" ? null : var.kms_key_arn
    }
    bucket_key_enabled = true
  }
}

# State must never be public.
resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Reject any non-TLS access to the state bucket.
resource "aws_s3_bucket_policy" "state_tls_only" {
  bucket = aws_s3_bucket.state.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyInsecureTransport"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource = [
        aws_s3_bucket.state.arn,
        "${aws_s3_bucket.state.arn}/*",
      ]
      Condition = {
        Bool = { "aws:SecureTransport" = "false" }
      }
    }]
  })
}

# ── Lock table ──────────────────────────────────────────────────────────────────
# DynamoDB table for state locking (prevents concurrent applies clobbering state).
resource "aws_dynamodb_table" "lock" {
  name         = var.lock_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}
