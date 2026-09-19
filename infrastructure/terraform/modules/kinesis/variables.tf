variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "stream_name" {
  description = "Name of the Kinesis data stream used for telemetry ingestion"
  type        = string
  default     = "cloudops-telemetry-stream"
}

variable "stream_mode" {
  description = "Kinesis capacity mode; ON_DEMAND avoids fixed shard cost in dev"
  type        = string
  default     = "ON_DEMAND"
}

variable "retention_period" {
  description = "Data record retention period in hours (24-8760); 24h minimum used for dev"
  type        = number
  default     = 24
}