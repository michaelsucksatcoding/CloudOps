variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "table_name" {
  description = "Name of the DynamoDB table used for hot/realtime telemetry storage"
  type        = string
  default     = "cloudops-telemetry-hot"
}

variable "billing_mode" {
  description = "DynamoDB billing mode; on-demand (PAY_PER_REQUEST) avoids idle capacity cost in dev"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "deletion_protection_enabled" {
  description = "Enable deletion protection on the DynamoDB table"
  type        = bool
  default     = false
}