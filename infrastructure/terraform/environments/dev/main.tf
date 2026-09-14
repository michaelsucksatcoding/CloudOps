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

  environment              = var.environment
  cluster_name             = var.cluster_name
  kubernetes_version       = var.kubernetes_version
  vpc_id                   = module.networking.vpc_id
  subnet_ids               = module.networking.private_subnet_ids
  control_plane_subnet_ids = concat(module.networking.public_subnet_ids, module.networking.private_subnet_ids)
  node_instance_types      = var.node_instance_types
  desired_nodes            = var.desired_nodes
  min_nodes                = var.min_nodes
  max_nodes                = var.max_nodes
}
