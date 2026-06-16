output "state_bucket" {
  description = "S3 bucket holding Terraform remote state — set as the environments' backend `bucket`."
  value       = aws_s3_bucket.state.id
}

output "lock_table" {
  description = "DynamoDB lock table — set as the environments' backend `dynamodb_table`."
  value       = aws_dynamodb_table.lock.name
}

output "region" {
  description = "Region of the state bucket — set as the environments' backend `region`."
  value       = var.aws_region
}

output "backend_config_hint" {
  description = "Drop-in backend block for environments/<env>/main.tf."
  value       = <<-EOT
    backend "s3" {
      bucket         = "${aws_s3_bucket.state.id}"
      key            = "monorepo/<env>/terraform.tfstate"
      region         = "${var.aws_region}"
      encrypt        = true
      dynamodb_table = "${aws_dynamodb_table.lock.name}"
    }
  EOT
}
