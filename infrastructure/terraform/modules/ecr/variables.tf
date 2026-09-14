variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "repository_names" {
  description = "List of ECR repository names to create"
  type        = list(string)
  default     = ["cloudops-api", "cloudops-ml", "cloudops-event-processor"]
}
