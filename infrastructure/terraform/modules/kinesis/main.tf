# -----------------------------------------------------------------------------
# Kinesis Data Stream for Telemetry Ingestion
# -----------------------------------------------------------------------------
resource "aws_kinesis_stream" "telemetry" {
  name             = var.stream_name
  retention_period = var.retention_period

  # AWS-managed server-side encryption (aws/kinesis KMS key); no custom KMS
  encryption_type = "KMS"
  kms_key_id      = "alias/aws/kinesis"

  stream_mode_details {
    stream_mode = var.stream_mode
  }

  tags = {
    Name        = var.stream_name
    Environment = var.environment
  }
}