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

variable "artifact_bucket_arn" {
  type        = string
  description = "ARN of the existing S3 bucket containing the built Flink JAR"
}

variable "artifact_key" {
  type    = string
  default = "flink/realtime-analytics-1.0.0.jar"
}

resource "aws_kinesis_stream" "events" {
  name        = "realtime-events-practice"
  shard_count = 2
}

resource "aws_opensearch_domain" "analytics" {
  domain_name    = "realtime-practice"
  engine_version = "OpenSearch_2.13"

  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
    volume_type = "gp3"
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
}

resource "aws_iam_role" "flink" {
  name_prefix = "flink-practice-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "kinesisanalytics.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "flink" {
  role = aws_iam_role.flink.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ReadKinesis"
        Effect = "Allow"

        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:ListShards"
        ]

        Resource = aws_kinesis_stream.events.arn
      },
      {
        Sid    = "ReadArtifact"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]

        Resource = "${var.artifact_bucket_arn}/${var.artifact_key}"
      },
      {
        Sid    = "WriteOpenSearch"
        Effect = "Allow"

        Action = [
          "es:ESHttpGet",
          "es:ESHttpPost",
          "es:ESHttpPut"
        ]

        Resource = "${aws_opensearch_domain.analytics.arn}/*"
      },
      {
        Sid    = "WriteLogs"
        Effect = "Allow"

        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogStream",
          "logs:CreateLogGroup"
        ]

        Resource = "*"
      }
    ]
  })
}

resource "aws_kinesisanalyticsv2_application" "job" {
  name                   = "realtime-analytics-practice"
  runtime_environment    = "FLINK-1_18"
  service_execution_role = aws_iam_role.flink.arn

  application_configuration {
    application_code_configuration {
      code_content {
        s3_content_location {
          bucket_arn = var.artifact_bucket_arn
          file_key   = var.artifact_key
        }
      }

      code_content_type = "ZIPFILE"
    }

    environment_properties {
      property_group {
        property_group_id = "runtime"

        property_map = {
          STREAM_NAME         = aws_kinesis_stream.events.name
          OPENSEARCH_ENDPOINT = aws_opensearch_domain.analytics.endpoint
        }
      }
    }
  }

  depends_on = [
    aws_iam_role_policy.flink
  ]
}

output "stream_name" {
  value = aws_kinesis_stream.events.name
}

output "opensearch_endpoint" {
  value = aws_opensearch_domain.analytics.endpoint
}