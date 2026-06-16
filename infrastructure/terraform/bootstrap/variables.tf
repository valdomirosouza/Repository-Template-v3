variable "aws_region" {
  description = "AWS region for the state bucket and lock table (must match the environments' backend region)."
  type        = string
  default     = "us-east-1"
}

variable "state_bucket_name" {
  description = "Globally-unique S3 bucket name for Terraform remote state. Replace the org placeholder."
  type        = string
  default     = "your-org-terraform-state"
}

variable "lock_table_name" {
  description = "DynamoDB table name for state locking (matches the environments' backend dynamodb_table)."
  type        = string
  default     = "terraform-state-lock"
}

variable "kms_key_arn" {
  description = "Optional KMS key ARN for state encryption. Empty string uses SSE-S3 (AES256)."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags merged into the provider default_tags."
  type        = map(string)
  default     = {}
}
