terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
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

variable "subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for the Redshift Serverless workgroup"
}

variable "security_group_ids" {
  type        = list(string)
  description = "Security group IDs for the Redshift Serverless workgroup"
}

resource "random_password" "admin" {
  length  = 24
  special = false
}

resource "aws_s3_bucket" "landing" {
  bucket_prefix = "warehouse-practice-"
}

resource "aws_s3_bucket_public_access_block" "landing" {
  bucket = aws_s3_bucket.landing.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_role" "redshift" {
  name_prefix = "redshift-practice-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = [
            "redshift.amazonaws.com",
            "redshift-serverless.amazonaws.com"
          ]
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "redshift" {
  role = aws_iam_role.redshift.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ListLandingBucket"
        Effect = "Allow"

        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]

        Resource = aws_s3_bucket.landing.arn
      },
      {
        Sid    = "ReadLandingObjects"
        Effect = "Allow"

        Action = [
          "s3:GetObject"
        ]

        Resource = "${aws_s3_bucket.landing.arn}/*"
      }
    ]
  })
}

resource "aws_redshiftserverless_namespace" "lab" {
  namespace_name = "warehouse-practice"
  db_name        = "dev"

  admin_username      = "labadmin"
  admin_user_password = random_password.admin.result

  iam_roles = [
    aws_iam_role.redshift.arn
  ]
}

resource "aws_redshiftserverless_workgroup" "lab" {
  workgroup_name = "warehouse-practice"
  namespace_name = aws_redshiftserverless_namespace.lab.namespace_name

  base_capacity = 8

  subnet_ids         = var.subnet_ids
  security_group_ids = var.security_group_ids

  publicly_accessible = false
}

output "endpoint" {
  value = aws_redshiftserverless_workgroup.lab.endpoint[0].address
}

output "landing_bucket" {
  value = aws_s3_bucket.landing.id
}

output "admin_password" {
  value     = random_password.admin.result
  sensitive = true
}

output "redshift_role_arn" {
  value = aws_iam_role.redshift.arn
}