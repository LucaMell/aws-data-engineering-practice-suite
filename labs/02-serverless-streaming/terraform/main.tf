terraform {
  required_providers {
    aws = { source="hashicorp/aws", version="~> 5.0" }
    archive = { source="hashicorp/archive", version="~> 2.0" }
  }
}
provider "aws" { region="eu-west-1" }
resource "aws_kinesis_stream" "events" {
  name="serverless-events-practice"
  shard_count=1
}
resource "aws_s3_bucket" "output" { bucket_prefix="serverless-output-practice-" }
resource "aws_sqs_queue" "quarantine" { name="serverless-quarantine-practice" }
resource "aws_sns_topic" "alerts" { name="serverless-alerts-practice" }
data "archive_file" "lambda" {
  type="zip"
  source_file="${path.module}/../handler.py"
  output_path="${path.module}/handler.zip"
}
resource "aws_iam_role" "lambda" {
  name_prefix="serverless-practice-"
  assume_role_policy=jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="lambda.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy" "lambda" {
  role=aws_iam_role.lambda.id
  policy=jsonencode({Version="2012-10-17",Statement=[
    {Effect="Allow",Action=["kinesis:GetRecords","kinesis:GetShardIterator","kinesis:DescribeStream","kinesis:DescribeStreamSummary","kinesis:ListShards"],Resource=aws_kinesis_stream.events.arn},
    {Effect="Allow",Action=["s3:PutObject"],Resource="${aws_s3_bucket.output.arn}/*"},
    {Effect="Allow",Action=["sqs:SendMessage"],Resource=aws_sqs_queue.quarantine.arn},
    {Effect="Allow",Action=["sns:Publish"],Resource=aws_sns_topic.alerts.arn},
    {Effect="Allow",Action=["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],Resource="*"}]})
}
resource "aws_lambda_function" "processor" {
  function_name="serverless-stream-practice"
  role=aws_iam_role.lambda.arn
  runtime="python3.12"
  handler="handler.lambda_handler"
  filename=data.archive_file.lambda.output_path
  source_code_hash=data.archive_file.lambda.output_base64sha256
  environment {
    variables={BUCKET=aws_s3_bucket.output.id,QUEUE_URL=aws_sqs_queue.quarantine.url,TOPIC_ARN=aws_sns_topic.alerts.arn}
  }
}
resource "aws_lambda_event_source_mapping" "trigger" {
  event_source_arn=aws_kinesis_stream.events.arn
  function_name=aws_lambda_function.processor.arn
  starting_position="TRIM_HORIZON"
  function_response_types=["ReportBatchItemFailures"]
}
output "stream_name" { value=aws_kinesis_stream.events.name }
