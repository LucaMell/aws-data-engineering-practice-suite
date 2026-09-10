terraform { required_providers { aws={source="hashicorp/aws",version="~> 5.0"}, random={source="hashicorp/random",version="~> 3.0"} } }
provider "aws" { region="eu-west-1" }
variable "subnet_ids" { type=list(string) }
variable "security_group_ids" { type=list(string) }
resource "random_password" "admin" { length=24
  special=false }
resource "aws_s3_bucket" "landing" { bucket_prefix="warehouse-practice-" }
resource "aws_iam_role" "redshift" {
  name_prefix="redshift-practice-"
  assume_role_policy=jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="redshift.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy" "redshift" {
  role=aws_iam_role.redshift.id
  policy=jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Action=["s3:GetObject","s3:ListBucket"],Resource=[aws_s3_bucket.landing.arn,"${aws_s3_bucket.landing.arn}/*"]}]})
}
resource "aws_redshiftserverless_namespace" "lab" {
  namespace_name="warehouse-practice"
  db_name="dev"
  admin_username="labadmin"
  admin_user_password=random_password.admin.result
  iam_roles=[aws_iam_role.redshift.arn]
}
resource "aws_redshiftserverless_workgroup" "lab" {
  workgroup_name="warehouse-practice"
  namespace_name=aws_redshiftserverless_namespace.lab.namespace_name
  base_capacity=8
  subnet_ids=var.subnet_ids
  security_group_ids=var.security_group_ids
  publicly_accessible=false
}
output "endpoint" { value=aws_redshiftserverless_workgroup.lab.endpoint[0].address }
output "landing_bucket" { value=aws_s3_bucket.landing.id }
output "admin_password" { value=random_password.admin.result, sensitive=true }
output "redshift_role_arn" { value=aws_iam_role.redshift.arn }
