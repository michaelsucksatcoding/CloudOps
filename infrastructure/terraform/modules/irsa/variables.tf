variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "namespace" {
  description = "Kubernetes namespace hosting the service accounts"
  type        = string
}

variable "oidc_provider_arn" {
  description = "ARN of the EKS IAM OIDC provider"
  type        = string
}

variable "oidc_issuer" {
  description = "EKS OIDC issuer host (without https:// scheme) used in trust condition keys"
  type        = string
}

variable "api_service_account_name" {
  description = "Name of the API workload Kubernetes service account"
  type        = string
  default     = "cloudops-api"
}

variable "event_processor_service_account_name" {
  description = "Name of the event-processor workload Kubernetes service account"
  type        = string
  default     = "cloudops-event-processor"
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB hot-storage table"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 data-lake bucket"
  type        = string
}