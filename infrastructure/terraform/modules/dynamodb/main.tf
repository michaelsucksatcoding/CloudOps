# -----------------------------------------------------------------------------
# DynamoDB Hot Storage for Realtime Telemetry
# -----------------------------------------------------------------------------
resource "aws_dynamodb_table" "hot_telemetry" {
  name         = var.table_name
  billing_mode = var.billing_mode
  hash_key     = "service"
  range_key    = "timestamp"

  attribute {
    name = "service"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  # AWS-managed server-side encryption (DynamoDB-owned key)
  server_side_encryption {
    enabled = true
  }

  deletion_protection_enabled = var.deletion_protection_enabled

  tags = {
    Name        = var.table_name
    Environment = var.environment
  }
}