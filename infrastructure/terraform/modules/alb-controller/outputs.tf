output "role_arn" {
  description = "ARN of the Load Balancer Controller IRSA role"
  value       = aws_iam_role.lb.arn
}

output "role_name" {
  description = "Name of the Load Balancer Controller IRSA role"
  value       = aws_iam_role.lb.name
}

output "policy_arn" {
  description = "ARN of the Load Balancer Controller IAM policy"
  value       = aws_iam_policy.lb.arn
}