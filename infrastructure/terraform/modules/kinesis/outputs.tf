output "stream_name" {
  description = "Name of the Kinesis telemetry stream"
  value       = aws_kinesis_stream.telemetry.name
}

output "stream_arn" {
  description = "ARN of the Kinesis telemetry stream"
  value       = aws_kinesis_stream.telemetry.arn
}

output "stream_id" {
  description = "ID of the Kinesis telemetry stream"
  value       = aws_kinesis_stream.telemetry.id
}