terraform {
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}
provider "aws" { region = var.region }
variable "region" {
  type = string
  default = "eu-west-1"
}
variable "name" {
  type = string
  default = "batch-lake-practice"
}
resource "aws_s3_bucket" "data" { bucket_prefix = "${var.name}-data-" }
resource "aws_s3_bucket" "scripts" { bucket_prefix = "${var.name}-scripts-" }
resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}
resource "aws_s3_object" "script" {
  bucket = aws_s3_bucket.scripts.id
  key = "glue/glue_job.py"
  source = "${path.module}/../glue_job.py"
  etag = filemd5("${path.module}/../glue_job.py")
}
resource "aws_iam_role" "glue" {
  name_prefix = "${var.name}-"
  assume_role_policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="glue.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy_attachment" "glue" {
  role = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}
resource "aws_iam_role_policy" "buckets" {
  role = aws_iam_role.glue.id
  policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Action=["s3:GetObject","s3:PutObject","s3:DeleteObject"],Resource=["${aws_s3_bucket.data.arn}/*","${aws_s3_bucket.scripts.arn}/*"]}]})
}
resource "aws_glue_catalog_database" "lab" { name = replace(var.name,"-","_") }
resource "aws_glue_job" "job" {
  name = var.name
  role_arn = aws_iam_role.glue.arn
  glue_version = "5.0"
  worker_type = "G.1X"
  number_of_workers = 2
  command {
    name = "glueetl"
    python_version = "3"
    script_location = "s3://${aws_s3_bucket.scripts.id}/${aws_s3_object.script.key}"
  }
  default_arguments = {
    "--INPUT_PATH" = "s3://${aws_s3_bucket.data.id}/bronze/"
    "--OUTPUT_PATH" = "s3://${aws_s3_bucket.data.id}/silver/"
  }
}
output "data_bucket" { value = aws_s3_bucket.data.id }

