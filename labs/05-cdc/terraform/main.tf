terraform { required_providers { aws={source="hashicorp/aws",version="~> 5.0"} } }
provider "aws" { region="eu-west-1" }
variable "source_endpoint_arn" {
  type = string
  description = "Existing RDS PostgreSQL DMS source endpoint ARN"
}
variable "replication_subnet_group_id" { type=string }
variable "vpc_security_group_ids" { type=list(string) }
resource "aws_s3_bucket" "cdc" { bucket_prefix="dms-cdc-practice-" }
resource "aws_iam_role" "dms_s3" {
  name_prefix="dms-s3-practice-"
  assume_role_policy=jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="dms.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy" "dms_s3" {
  role=aws_iam_role.dms_s3.id
  policy=jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Action=["s3:PutObject","s3:DeleteObject","s3:GetObject"],Resource="${aws_s3_bucket.cdc.arn}/*"},{Effect="Allow",Action="s3:ListBucket",Resource=aws_s3_bucket.cdc.arn}]})
}
resource "aws_dms_endpoint" "s3" {
  endpoint_id="cdc-s3-practice"
  endpoint_type="target"
  engine_name="s3"
  s3_settings { bucket_name=aws_s3_bucket.cdc.id
  service_access_role_arn=aws_iam_role.dms_s3.arn
  data_format="parquet"
  timestamp_column_name="dms_timestamp" }
}
resource "aws_dms_replication_instance" "lab" {
  replication_instance_id="cdc-practice"
  replication_instance_class="dms.t3.micro"
  allocated_storage=20
  publicly_accessible=false
  replication_subnet_group_id=var.replication_subnet_group_id
  vpc_security_group_ids=var.vpc_security_group_ids
}
resource "aws_dms_replication_task" "lab" {
  replication_task_id="cdc-practice"
  migration_type="full-load-and-cdc"
  replication_instance_arn=aws_dms_replication_instance.lab.replication_instance_arn
  source_endpoint_arn=var.source_endpoint_arn
  target_endpoint_arn=aws_dms_endpoint.s3.endpoint_arn
  table_mappings=jsonencode({rules=[{"rule-type"="selection","rule-id"="1","rule-name"="customers","object-locator"={"schema-name"="public","table-name"="customers"},"rule-action"="include"}]})
}
