variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Target deployment environment"
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "cloudops-eks-dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "kubernetes_version" {
  description = "Kubernetes control plane version"
  type        = string
  default     = "1.31"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS worker nodes (sandbox account only permits Free-Tier-eligible types)"
  type        = list(string)
  default     = ["m7i-flex.large", "t3.small"]
}

variable "node_ami_type" {
  description = "EKS worker node AMI type (AL2023_x86_64_STANDARD used because default AL2 AMI is no longer published for EKS 1.30)"
  type        = string
  default     = "AL2023_x86_64_STANDARD"
}

variable "desired_nodes" {
  description = "Desired number of worker nodes in node group"
  type        = number
  default     = 2
}

variable "min_nodes" {
  description = "Minimum number of worker nodes in node group"
  type        = number
  default     = 2
}

variable "max_nodes" {
  description = "Maximum number of worker nodes in node group"
  type        = number
  default     = 4
}

variable "lambda_image_tag" {
  description = "Container image tag for the Lambda event-processor function"
  type        = string
  default     = "latest"
}

variable "workload_namespace" {
  description = "Kubernetes namespace hosting the CloudOps workloads"
  type        = string
  default     = "cloudops-dev"
}

variable "cluster_public_access_cidrs" {
  description = <<-EOT
    CIDR blocks allowed to reach the EKS public API endpoint.
    Kept open (0.0.0.0/0) for dev tooling by default; this MUST be narrowed to
    the operator's CIDR(s) before production use.
  EOT
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enabled_cluster_log_types" {
  description = "EKS control plane log types to enable (api, audit, authenticator, controllerManager, scheduler)"
  type        = list(string)
  default     = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}
