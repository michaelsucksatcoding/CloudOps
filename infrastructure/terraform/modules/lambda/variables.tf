variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for the Lambda function"
  type        = string
  default     = "us-east-1"
}

variable "function_name" {
  description = "Name of the Lambda event-processor function"
  type        = string
  default     = "cloudops-event-processor"
}

variable "image_uri" {
  description = "URI of the container image for the Lambda function"
  type        = string
}

variable "kinesis_stream_name" {
  description = "Name of the Kinesis telemetry stream consumed by Lambda"
  type        = string
}

variable "kinesis_stream_arn" {
  description = "ARN of the Kinesis telemetry stream consumed by Lambda"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB hot-storage table written by Lambda"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB hot-storage table written by Lambda"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 data-lake bucket written by Lambda"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 data-lake bucket written by Lambda"
  type        = string
}

variable "log_level" {
  description = "Application log level for the Lambda function"
  type        = string
  default     = "INFO"
}

variable "timeout" {
  description = "Lambda function execution timeout in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Lambda function memory allocation in MB"
  type        = number
  default     = 512
}

variable "log_retention_days" {
  description = "CloudWatch Log Group retention for the Lambda function's logs"
  type        = number
  default     = 7
}