# -----------------------------------------------------------------------------
# API Workload IAM Role (IRSA)
# -----------------------------------------------------------------------------
resource "aws_iam_role" "api" {
  name = "cloudops-api-irsa-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRoleWithWebIdentity"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${var.oidc_issuer}:aud" = "sts.amazonaws.com"
            "${var.oidc_issuer}:sub" = "system:serviceaccount:${var.namespace}:${var.api_service_account_name}"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "cloudops-api-irsa-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_iam_policy" "api_kinesis_write" {
  name = "cloudops-api-kinesis-write-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "KinesisWrite"
        Effect = "Allow"
        Action = [
          "kinesis:PutRecord",
          "kinesis:PutRecords",
        ]
        Resource = var.kinesis_stream_arn
      }
    ]
  })

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "api_kinesis_write" {
  policy_arn = aws_iam_policy.api_kinesis_write.arn
  role       = aws_iam_role.api.name
}

# -----------------------------------------------------------------------------
# Event Processor Workload IAM Role (IRSA)
# -----------------------------------------------------------------------------
resource "aws_iam_role" "event_processor" {
  name = "cloudops-event-processor-irsa-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRoleWithWebIdentity"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${var.oidc_issuer}:aud" = "sts.amazonaws.com"
            "${var.oidc_issuer}:sub" = "system:serviceaccount:${var.namespace}:${var.event_processor_service_account_name}"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "cloudops-event-processor-irsa-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_iam_policy" "event_processor_data_access" {
  name = "cloudops-event-processor-data-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DynamoDBHotStore"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
        ]
        Resource = var.dynamodb_table_arn
      },
      {
        Sid    = "S3DataLake"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
        ]
        Resource = "${var.s3_bucket_arn}/*"
      }
    ]
  })

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "event_processor_data_access" {
  policy_arn = aws_iam_policy.event_processor_data_access.arn
  role       = aws_iam_role.event_processor.name
}