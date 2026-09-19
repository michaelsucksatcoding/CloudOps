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
  repository_names = ["cloudops-api", "cloudops-ml", "cloudops-event-processor", "cloudops-event-processor-lambda"]
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
}

module "dynamodb" {
  source = "../../modules/dynamodb"

  environment = var.environment
}

module "kinesis" {
  source = "../../modules/kinesis"

  environment = var.environment
}

module "s3" {
  source = "../../modules/s3"

  environment = var.environment
}

module "lambda" {
  source = "../../modules/lambda"

  environment         = var.environment
  aws_region          = var.aws_region
  image_uri           = "${module.ecr.repository_urls["cloudops-event-processor-lambda"]}:${var.lambda_image_tag}"
  kinesis_stream_name = module.kinesis.stream_name
  kinesis_stream_arn  = module.kinesis.stream_arn
  dynamodb_table_name = module.dynamodb.table_name
  dynamodb_table_arn  = module.dynamodb.table_arn
  s3_bucket_name      = module.s3.bucket_name
  s3_bucket_arn       = module.s3.bucket_arn
}

module "irsa" {
  source = "../../modules/irsa"

  environment        = var.environment
  namespace          = var.workload_namespace
  oidc_provider_arn  = module.eks.oidc_provider_arn
  oidc_issuer        = replace(module.eks.oidc_provider_url, "https://", "")
  kinesis_stream_arn = module.kinesis.stream_arn
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
