terraform {
  required_version = ">= 1.7.0"

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


# --------------------------------------------------
# Variables
# --------------------------------------------------

variable "region" {
  description = "AWS region where resources are created."
  type        = string
  default     = "eu-west-1"
}

variable "name" {
  description = "Name used for the practice resources."
  type        = string
  default     = "batch-lake-practice"
}


# --------------------------------------------------
# Common tags
# --------------------------------------------------

locals {
  common_tags = {
    Project     = var.name
    Environment = "practice"
  }
}


# --------------------------------------------------
# S3 data bucket
#
# This bucket stores:
# bronze/orders.csv
# silver/orders.parquet
# --------------------------------------------------

resource "aws_s3_bucket" "data" {
  bucket_prefix = "${var.name}-data-"

  tags = merge(local.common_tags, {
    Purpose = "Data"
  })
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# --------------------------------------------------
# S3 scripts bucket
#
# This bucket stores:
# glue/glue_job.py
#
# We keep this because Terraform already created it.
# --------------------------------------------------

resource "aws_s3_bucket" "scripts" {
  bucket_prefix = "${var.name}-scripts-"

  tags = merge(local.common_tags, {
    Purpose = "Glue scripts"
  })
}

resource "aws_s3_bucket_public_access_block" "scripts" {
  bucket = aws_s3_bucket.scripts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# --------------------------------------------------
# Upload the Glue script to the scripts bucket
#
# The Glue job cannot run on the AWS Free account
# plan, but we keep the script as a project artifact.
# --------------------------------------------------

resource "aws_s3_object" "script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "glue/glue_job.py"
  source = "${path.module}/../glue_job.py"

  etag = filemd5("${path.module}/../glue_job.py")
}


# --------------------------------------------------
# IAM role for Glue
#
# The role is kept because it was already created.
# IAM roles themselves do not run anything.
# --------------------------------------------------

resource "aws_iam_role" "glue" {
  name_prefix = "${var.name}-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "glue.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}


# --------------------------------------------------
# Standard AWS Glue permissions
# --------------------------------------------------

resource "aws_iam_role_policy_attachment" "glue" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}


# --------------------------------------------------
# Permissions for accessing the two S3 buckets
# --------------------------------------------------

resource "aws_iam_role_policy" "buckets" {
  name = "${var.name}-s3-access"
  role = aws_iam_role.glue.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:ListBucket"
        ]

        Resource = [
          aws_s3_bucket.data.arn,
          aws_s3_bucket.scripts.arn
        ]
      },
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]

        Resource = [
          "${aws_s3_bucket.data.arn}/*",
          "${aws_s3_bucket.scripts.arn}/*"
        ]
      }
    ]
  })
}


# --------------------------------------------------
# Glue Data Catalog database
#
# This is metadata only. It does not execute a job.
# --------------------------------------------------

resource "aws_glue_catalog_database" "lab" {
  name        = replace(var.name, "-", "_")
  description = "Data Catalog database for the batch lake practice project."
}


# --------------------------------------------------
# Outputs
# --------------------------------------------------

output "data_bucket" {
  description = "S3 bucket containing Bronze and Silver data."
  value       = aws_s3_bucket.data.id
}

output "scripts_bucket" {
  description = "S3 bucket containing project scripts."
  value       = aws_s3_bucket.scripts.id
}

output "catalog_database" {
  description = "Glue Data Catalog database name."
  value       = aws_glue_catalog_database.lab.name
}