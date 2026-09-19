output "table_name" {
  description = "Name of the DynamoDB hot storage table"
  value       = aws_dynamodb_table.hot_telemetry.name
}

output "table_arn" {
  description = "ARN of the DynamoDB hot storage table"
  value       = aws_dynamodb_table.hot_telemetry.arn
}

output "table_id" {
  description = "ID of the DynamoDB hot storage table"
  value       = aws_dynamodb_table.hot_telemetry.id
}