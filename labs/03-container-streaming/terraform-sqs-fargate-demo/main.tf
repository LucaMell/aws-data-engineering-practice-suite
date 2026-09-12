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

variable "desired_count" {
  type        = number
  default     = 0
  description = "Number of Fargate workers. Keep at 0 until the image is pushed."

  validation {
    condition     = contains([0, 1], var.desired_count)
    error_message = "This short demo permits only 0 or 1 task."
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_iam_policy_document" "ecs_tasks" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_ecr_repository" "worker" {
  name         = "lab3-container-stream-worker"
  force_delete = true
}

resource "aws_s3_bucket" "output" {
  bucket_prefix = "lab3-ecs-output-"
  force_destroy = true
}

resource "aws_sqs_queue" "input" {
  name                       = "lab3-ecs-input"
  visibility_timeout_seconds = 30
  receive_wait_time_seconds  = 5
}

resource "aws_sqs_queue" "quarantine" {
  name = "lab3-ecs-quarantine"
}

resource "aws_sqs_queue" "alert_capture" {
  name = "lab3-ecs-alert-capture"
}

resource "aws_sns_topic" "alerts" {
  name = "lab3-ecs-alerts"
}

data "aws_iam_policy_document" "alert_capture" {
  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.alert_capture.arn]

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.alerts.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "alert_capture" {
  queue_url = aws_sqs_queue.alert_capture.id
  policy    = data.aws_iam_policy_document.alert_capture.json
}

resource "aws_sns_topic_subscription" "alert_capture" {
  topic_arn            = aws_sns_topic.alerts.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.alert_capture.arn
  raw_message_delivery = true

  depends_on = [aws_sqs_queue_policy.alert_capture]
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/lab3-sqs-fargate-demo"
  retention_in_days = 1
}

resource "aws_ecs_cluster" "lab" {
  name = "lab3-sqs-fargate-demo"
}

resource "aws_iam_role" "task" {
  name_prefix        = "lab3-ecs-task-"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks.json
}

resource "aws_iam_role_policy" "task" {
  role = aws_iam_role.task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]

        Resource = aws_sqs_queue.input.arn
      },
      {
        Effect   = "Allow"
        Action   = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.quarantine.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.output.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["sns:Publish"]
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}

resource "aws_iam_role" "execution" {
  name_prefix        = "lab3-ecs-execution-"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks.json
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "lab3-sqs-fargate-demo"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512

  task_role_arn      = aws_iam_role.task.arn
  execution_role_arn = aws_iam_role.execution.arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = "${aws_ecr_repository.worker.repository_url}:lab3"
      essential = true

      environment = [
        {
          name  = "INPUT_MODE"
          value = "sqs"
        },
        {
          name  = "INPUT_QUEUE_URL"
          value = aws_sqs_queue.input.url
        },
        {
          name  = "BUCKET"
          value = aws_s3_bucket.output.id
        },
        {
          name  = "QUEUE_URL"
          value = aws_sqs_queue.quarantine.url
        },
        {
          name  = "TOPIC_ARN"
          value = aws_sns_topic.alerts.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.worker.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "worker"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "worker" {
  name            = "lab3-sqs-fargate-demo"
  cluster         = aws_ecs_cluster.lab.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    assign_public_ip = true
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.worker.repository_url
}

output "input_queue_url" {
  value = aws_sqs_queue.input.url
}

output "quarantine_queue_url" {
  value = aws_sqs_queue.quarantine.url
}

output "alert_capture_queue_url" {
  value = aws_sqs_queue.alert_capture.url
}

output "output_bucket" {
  value = aws_s3_bucket.output.id
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.lab.name
}

output "ecs_service_name" {
  value = aws_ecs_service.worker.name
}
