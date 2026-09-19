# -----------------------------------------------------------------------------
# Lambda Event Processor IAM Execution Role
# -----------------------------------------------------------------------------
resource "aws_iam_role" "lambda" {
  name = "cloudops-lambda-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "cloudops-lambda-${var.environment}"
    Environment = var.environment
  }
}

# CloudWatch Logs for Lambda execution (AWS-provided minimal logging role)
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda.name
}

# CloudWatch Log Group with retention so Lambda logs are retained (and expire)
# on a schedule instead of accumulating indefinitely.
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Environment = var.environment
  }
}

# Least-privilege data access scoped to the specific stream, table, and bucket
resource "aws_iam_policy" "lambda_data_access" {
  name = "cloudops-lambda-data-access-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "KinesisRead"
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStreamSummary",
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:ListShards",
        ]
        Resource = var.kinesis_stream_arn
      },
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
      },
    ]
  })

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "lambda_data_access" {
  policy_arn = aws_iam_policy.lambda_data_access.arn
  role       = aws_iam_role.lambda.name
}

# -----------------------------------------------------------------------------
# Lambda Function (container image)
# -----------------------------------------------------------------------------
resource "aws_lambda_function" "event_processor" {
  function_name = var.function_name
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = var.image_uri
  timeout       = var.timeout
  memory_size   = var.memory_size

  environment {
    variables = {
      ENVIRONMENT           = var.environment
      AWS_REGION            = var.aws_region
      LOG_LEVEL             = var.log_level
      TELEMETRY_STREAM_NAME = var.kinesis_stream_name
      S3_DATA_LAKE_BUCKET   = var.s3_bucket_name
      DYNAMODB_HOT_TABLE    = var.dynamodb_table_name
    }
  }

  tags = {
    Name        = var.function_name
    Environment = var.environment
  }
}

# -----------------------------------------------------------------------------
# Kinesis -> Lambda Event Source Mapping
# -----------------------------------------------------------------------------
resource "aws_lambda_event_source_mapping" "kinesis" {
  event_source_arn  = var.kinesis_stream_arn
  function_name     = aws_lambda_function.event_processor.arn
  starting_position = "LATEST"
}