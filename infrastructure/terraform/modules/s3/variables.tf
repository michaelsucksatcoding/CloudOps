variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "bucket_name" {
  description = "Name of the S3 data-lake bucket for cold telemetry storage"
  type        = string
  default     = "cloudops-telemetry-lake"
}

variable "force_destroy" {
  description = "Allow Terraform destroy to delete the bucket even if it contains objects (DEV convenience)"
  type        = bool
  default     = true
}