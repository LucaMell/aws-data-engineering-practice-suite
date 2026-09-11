terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
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

variable "eks_oidc_provider_arn" {
  type        = string
  description = "ARN of the EKS OIDC identity provider"
}

variable "eks_oidc_issuer_host" {
  type        = string
  description = "EKS OIDC issuer hostname without https://"
}

variable "namespace" {
  type    = string
  default = "default"
}

resource "aws_kinesis_stream" "events" {
  name        = "kcl-events-practice"
  shard_count = 2
}

resource "aws_s3_bucket" "output" {
  bucket_prefix = "kcl-output-practice-"
}

resource "aws_sqs_queue" "quarantine" {
  name = "kcl-quarantine-practice"
}

resource "aws_sns_topic" "alerts" {
  name = "kcl-alerts-practice"
}

resource "aws_iam_role" "pod" {
  name_prefix = "kcl-pod-practice-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Federated = var.eks_oidc_provider_arn
        }

        Action = "sts:AssumeRoleWithWebIdentity"

        Condition = {
          StringEquals = {
            "${var.eks_oidc_issuer_host}:sub" = "system:serviceaccount:${var.namespace}:kcl-worker"
            "${var.eks_oidc_issuer_host}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "pod" {
  role = aws_iam_role.pod.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ReadKinesis"
        Effect = "Allow"

        Action = [
          "kinesis:DescribeStream",
          "kinesis:DescribeStreamSummary",
          "kinesis:ListShards",
          "kinesis:GetRecords",
          "kinesis:GetShardIterator"
        ]

        Resource = aws_kinesis_stream.events.arn
      },
      {
        Sid    = "ManageKCLState"
        Effect = "Allow"

        Action = [
          "dynamodb:CreateTable",
          "dynamodb:DescribeTable",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan"
        ]

        Resource = "arn:aws:dynamodb:${var.region}:*:table/booking-kcl-practice*"
      },
      {
        Sid      = "WriteOutput"
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.output.arn}/*"
      },
      {
        Sid      = "WriteQuarantine"
        Effect   = "Allow"
        Action   = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.quarantine.arn
      },
      {
        Sid      = "PublishAlerts"
        Effect   = "Allow"
        Action   = ["sns:Publish"]
        Resource = aws_sns_topic.alerts.arn
      },
      {
        Sid      = "PublishMetrics"
        Effect   = "Allow"
        Action   = ["cloudwatch:PutMetricData"]
        Resource = "*"
      }
    ]
  })
}

output "stream_name" {
  value = aws_kinesis_stream.events.name
}

output "bucket" {
  value = aws_s3_bucket.output.id
}

output "queue_url" {
  value = aws_sqs_queue.quarantine.url
}

output "topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "pod_role_arn" {
  value = aws_iam_role.pod.arn
}