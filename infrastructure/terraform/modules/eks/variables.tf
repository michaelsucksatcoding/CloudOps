variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "cloudops-eks-dev"
}

variable "kubernetes_version" {
  description = "Desired Kubernetes version"
  type        = string
  default     = "1.30"
}

variable "vpc_id" {
  description = "VPC ID where the cluster and nodes will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "Private subnet IDs for EKS worker nodes"
  type        = list(string)
}

variable "control_plane_subnet_ids" {
  description = "Subnet IDs for the EKS control plane (usually all subnets)"
  type        = list(string)
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS managed node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_ami_type" {
  description = "EKS worker node AMI type (e.g. AL2_x86_64, AL2023_x86_64_STANDARD, AL2023_x86_64_EXTENDED)"
  type        = string
  default     = "AL2_x86_64"
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

variable "cluster_public_access_cidrs" {
  description = "CIDR blocks allowed to reach the EKS public API endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enabled_cluster_log_types" {
  description = "EKS control plane log types to enable (api, audit, authenticator, controllerManager, scheduler)"
  type        = list(string)
  default     = []
}

variable "github_deploy_role_arn" {
  description = "IAM role ARN used by GitHub Actions CD to install/upgrade Helm releases in the EKS cluster. When set, a namespace-scoped EKS access entry granting AmazonEKS_EditPolicy is created so the role can manage Kubernetes resources in the listed github_deploy_namespaces without cluster-admin privileges. Empty by default so environments not deploying via GitHub Actions are unaffected."
  type        = string
  default     = ""
}

variable "github_deploy_namespaces" {
  description = "Kubernetes namespaces the GitHub deploy role is granted AmazonEKS_EditPolicy access to"
  type        = list(string)
  default     = ["cloudops-dev", "cloudops-monitoring"]
}

variable "authentication_mode" {
  description = "EKS cluster authentication mode. API_AND_CONFIG_MAP enables native EKS Access Entries together with the legacy aws-auth ConfigMap."
  type        = string
  default     = "API_AND_CONFIG_MAP"
}
