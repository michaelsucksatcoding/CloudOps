output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "Public Subnet IDs"
  value       = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private Subnet IDs"
  value       = module.networking.private_subnet_ids
}

output "ecr_repository_urls" {
  description = "ECR Repository URLs for container image publishing"
  value       = module.ecr.repository_urls
}

output "eks_cluster_name" {
  description = "EKS Cluster Name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS Cluster API Endpoint"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "eks_oidc_provider_arn" {
  description = "EKS OIDC Provider ARN for IAM Roles for Service Accounts (IRSA)"
  value       = module.eks.oidc_provider_arn
}

output "dynamodb_hot_table_name" {
  description = "Name of the DynamoDB hot storage table"
  value       = module.dynamodb.table_name
}

output "dynamodb_hot_table_arn" {
  description = "ARN of the DynamoDB hot storage table"
  value       = module.dynamodb.table_arn
}

output "kinesis_stream_name" {
  description = "Name of the Kinesis telemetry stream"
  value       = module.kinesis.stream_name
}

output "kinesis_stream_arn" {
  description = "ARN of the Kinesis telemetry stream"
  value       = module.kinesis.stream_arn
}

output "s3_data_lake_bucket_name" {
  description = "Name of the S3 data-lake bucket"
  value       = module.s3.bucket_name
}

output "s3_data_lake_bucket_arn" {
  description = "ARN of the S3 data-lake bucket"
  value       = module.s3.bucket_arn
}

output "lambda_function_name" {
  description = "Name of the Lambda event-processor function"
  value       = module.lambda.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda event-processor function"
  value       = module.lambda.function_arn
}

output "api_irsa_role_arn" {
  description = "ARN of the API workload IRSA role"
  value       = module.irsa.api_role_arn
}

output "event_processor_irsa_role_arn" {
  description = "ARN of the event-processor workload IRSA role"
  value       = module.irsa.event_processor_role_arn
}

output "alb_controller_role_arn" {
  description = "ARN of the AWS Load Balancer Controller IRSA role"
  value       = module.alb_controller.role_arn
}
