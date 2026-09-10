terraform { required_providers { aws={source="hashicorp/aws",version="~> 5.0"} } }
provider "aws" { region="eu-west-1" }
variable "image_uri" {
  type = string
  description = "ECR image URI created before apply"
}
data "aws_vpc" "default" { default=true }
data "aws_subnets" "default" { filter { name="vpc-id", values=[data.aws_vpc.default.id] } }
resource "aws_kinesis_stream" "events" { name="ecs-events-practice", shard_count=1 }
resource "aws_s3_bucket" "output" { bucket_prefix="ecs-output-practice-" }
resource "aws_sqs_queue" "quarantine" { name="ecs-quarantine-practice" }
resource "aws_sns_topic" "alerts" { name="ecs-alerts-practice" }
resource "aws_ecs_cluster" "lab" { name="data-practice" }
resource "aws_cloudwatch_log_group" "worker" { name="/ecs/data-practice"
  retention_in_days=7 }
resource "aws_iam_role" "task" {
  name_prefix="ecs-data-practice-"
  assume_role_policy=jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="ecs-tasks.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy" "task" {
  role=aws_iam_role.task.id
  policy=jsonencode({Version="2012-10-17",Statement=[
    {Effect="Allow",Action=["kinesis:ListShards","kinesis:GetShardIterator","kinesis:GetRecords"],Resource=aws_kinesis_stream.events.arn},
    {Effect="Allow",Action="s3:PutObject",Resource="${aws_s3_bucket.output.arn}/*"},
    {Effect="Allow",Action="sqs:SendMessage",Resource=aws_sqs_queue.quarantine.arn},
    {Effect="Allow",Action="sns:Publish",Resource=aws_sns_topic.alerts.arn}]})
}
resource "aws_iam_role" "execution" {
  name_prefix="ecs-execution-practice-"
  assume_role_policy=aws_iam_role.task.assume_role_policy
}
resource "aws_iam_role_policy_attachment" "execution" { role=aws_iam_role.execution.name, policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" }
resource "aws_ecs_task_definition" "worker" {
  family="data-practice"
  network_mode="awsvpc"
  requires_compatibilities=["FARGATE"]
  cpu=256
  memory=512
  task_role_arn=aws_iam_role.task.arn
  execution_role_arn=aws_iam_role.execution.arn
  container_definitions=jsonencode([{name="worker",image=var.image_uri,essential=true,environment=[
    {name="STREAM_NAME",value=aws_kinesis_stream.events.name},{name="BUCKET",value=aws_s3_bucket.output.id},
    {name="QUEUE_URL",value=aws_sqs_queue.quarantine.url},{name="TOPIC_ARN",value=aws_sns_topic.alerts.arn}],
    logConfiguration={logDriver="awslogs",options={"awslogs-group"=aws_cloudwatch_log_group.worker.name,"awslogs-region"="eu-west-1","awslogs-stream-prefix"="worker"}}}])
}
resource "aws_ecs_service" "worker" {
  name="data-practice"
  cluster=aws_ecs_cluster.lab.id
  task_definition=aws_ecs_task_definition.worker.arn
  desired_count=1
  launch_type="FARGATE"
  network_configuration { subnets=data.aws_subnets.default.ids
  assign_public_ip=true }
}
