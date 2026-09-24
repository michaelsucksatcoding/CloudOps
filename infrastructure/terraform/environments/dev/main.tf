# =============================================================================
# CloudOps AI - Dev Environment Terraform Root Module
# =============================================================================

module "networking" {
  source = "../../modules/networking"

  environment          = var.environment
  cluster_name         = var.cluster_name
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "ecr" {
  source = "../../modules/ecr"

  environment      = var.environment
  repository_names = ["cloudops-api", "cloudops-ml", "cloudops-event-processor"]
}

module "eks" {
  source = "../../modules/eks"

  environment                 = var.environment
  cluster_name                = var.cluster_name
  kubernetes_version          = var.kubernetes_version
  vpc_id                      = module.networking.vpc_id
  subnet_ids                  = module.networking.private_subnet_ids
  control_plane_subnet_ids    = concat(module.networking.public_subnet_ids, module.networking.private_subnet_ids)
  node_instance_types         = var.node_instance_types
  node_ami_type               = var.node_ami_type
  desired_nodes               = var.desired_nodes
  min_nodes                   = var.min_nodes
  max_nodes                   = var.max_nodes
  cluster_public_access_cidrs = var.cluster_public_access_cidrs
  enabled_cluster_log_types   = var.enabled_cluster_log_types
  github_deploy_role_arn      = var.github_deploy_role_arn
  github_deploy_namespaces    = var.github_deploy_namespaces
}

module "dynamodb" {
  source = "../../modules/dynamodb"

  environment = var.environment
}

module "s3" {
  source = "../../modules/s3"

  environment = var.environment
}

module "irsa" {
  source = "../../modules/irsa"

  environment        = var.environment
  namespace          = var.workload_namespace
  oidc_provider_arn  = module.eks.oidc_provider_arn
  oidc_issuer        = replace(module.eks.oidc_provider_url, "https://", "")
  dynamodb_table_arn = module.dynamodb.table_arn
  s3_bucket_arn      = module.s3.bucket_arn
}

module "alb_controller" {
  source = "../../modules/alb-controller"

  environment       = var.environment
  namespace         = var.workload_namespace
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_issuer       = replace(module.eks.oidc_provider_url, "https://", "")
}
