# -----------------------------------------------------------------------------
# AWS Load Balancer Controller IRSA
# -----------------------------------------------------------------------------
variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider"
  type        = string
}

variable "oidc_issuer" {
  description = "EKS OIDC issuer URL without the https:// scheme"
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace hosting the Load Balancer Controller"
  type        = string
  default     = "cloudops-dev"
}

variable "service_account_name" {
  description = "Kubernetes ServiceAccount used by the Load Balancer Controller"
  type        = string
  default     = "aws-load-balancer-controller"
}