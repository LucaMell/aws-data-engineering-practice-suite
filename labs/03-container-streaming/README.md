# Lab 3: Container streaming on ECS/Fargate

The worker is long-running and polls Kinesis. Native deployment is an ECS task; Docker is the artifact; `kubernetes.yaml` shows the same container on EKS. Build and push to ECR, pass `-var image_uri=...`, apply Terraform, send `sample/event.json`, inspect ECS/CloudWatch/S3, then destroy.

The one-shard/one-task constraint is intentional. Use KCL (Lab 4) before horizontal scaling. Public IP/default VPC keeps the lab understandable; production should use private subnets and VPC endpoints.

