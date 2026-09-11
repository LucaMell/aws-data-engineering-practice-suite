terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "name" {
  type    = string
  default = "serverless-stream-practice"
}

variable "alert_email" {
  description = "Optional email address for SNS alerts"
  type        = string
  default     = ""
}


# Input queue: this replaces Kinesis on the Free plan.

resource "aws_sqs_queue" "events" {
  name                       = "${var.name}-events"
  visibility_timeout_seconds = 60
}


# Invalid business records are stored here.

resource "aws_sqs_queue" "quarantine" {
  name                      = "${var.name}-quarantine"
  message_retention_seconds = 345600
}


# Valid records are written to this bucket.

resource "aws_s3_bucket" "output" {
  bucket_prefix = "${var.name}-output-"
}

resource "aws_s3_bucket_public_access_block" "output" {
  bucket = aws_s3_bucket.output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# Alert topic.

resource "aws_sns_topic" "alerts" {
  name = "${var.name}-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  count = var.alert_email == "" ? 0 : 1

  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}


# Package handler.py into a ZIP file.

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../handler.py"
  output_path = "${path.module}/handler.zip"
}


# Lambda execution role.

resource "aws_iam_role" "lambda" {
  name_prefix = "${var.name}-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}


# Permission to write Lambda logs to CloudWatch.

resource "aws_iam_role_policy_attachment" "basic_execution" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# Permissions required by the application.

resource "aws_iam_role_policy" "lambda" {
  name_prefix = "${var.name}-"
  role        = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ConsumeInputQueue"
        Effect = "Allow"

        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]

        Resource = aws_sqs_queue.events.arn
      },
      {
        Sid      = "WriteValidEvents"
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.output.arn}/*"
      },
      {
        Sid      = "WriteInvalidEvents"
        Effect   = "Allow"
        Action   = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.quarantine.arn
      },
      {
        Sid      = "PublishAlerts"
        Effect   = "Allow"
        Action   = ["sns:Publish"]
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}


# Lambda function.

resource "aws_lambda_function" "processor" {
  function_name = var.name
  role          = aws_iam_role.lambda.arn

  runtime = "python3.12"
  handler = "handler.lambda_handler"

  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256

  timeout     = 30
  memory_size = 128

  environment {
    variables = {
      BUCKET    = aws_s3_bucket.output.id
      QUEUE_URL = aws_sqs_queue.quarantine.url
      TOPIC_ARN = aws_sns_topic.alerts.arn
    }
  }
}


# Connect the input SQS queue to Lambda.

resource "aws_lambda_event_source_mapping" "trigger" {
  event_source_arn = aws_sqs_queue.events.arn
  function_name    = aws_lambda_function.processor.arn

  batch_size                         = 10
  maximum_batching_window_in_seconds = 0
  function_response_types            = ["ReportBatchItemFailures"]

  depends_on = [
    aws_iam_role_policy.lambda
  ]
}


output "event_queue_url" {
  value = aws_sqs_queue.events.url
}

output "quarantine_queue_url" {
  value = aws_sqs_queue.quarantine.url
}

output "output_bucket" {
  value = aws_s3_bucket.output.id
}

output "alert_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.processor.function_name
}