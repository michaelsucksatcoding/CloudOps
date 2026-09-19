output "function_name" {
  description = "Name of the Lambda event-processor function"
  value       = aws_lambda_function.event_processor.function_name
}

output "function_arn" {
  description = "ARN of the Lambda event-processor function"
  value       = aws_lambda_function.event_processor.arn
}

output "function_qualified_arn" {
  description = "Qualified ARN (with version/alias) of the Lambda event-processor function"
  value       = aws_lambda_function.event_processor.qualified_arn
}

output "event_source_mapping_id" {
  description = "ID of the Kinesis event source mapping"
  value       = aws_lambda_event_source_mapping.kinesis.id
}