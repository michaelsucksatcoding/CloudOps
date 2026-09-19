output "api_role_arn" {
  description = "ARN of the API workload IRSA role"
  value       = aws_iam_role.api.arn
}

output "api_role_name" {
  description = "Name of the API workload IRSA role"
  value       = aws_iam_role.api.name
}

output "event_processor_role_arn" {
  description = "ARN of the event-processor workload IRSA role"
  value       = aws_iam_role.event_processor.arn
}

output "event_processor_role_name" {
  description = "Name of the event-processor workload IRSA role"
  value       = aws_iam_role.event_processor.name
}