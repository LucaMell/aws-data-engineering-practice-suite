# AWS Data Engineering Practice Suite

Seven isolated labs, ordered from simplest to most operationally demanding:

1. `01-batch-lake`: S3 → Glue/Spark → Athena
2. `02-serverless-streaming`: Kinesis → Lambda → S3/SQS/SNS
3. `03-container-streaming`: Kinesis → ECS/Fargate worker → S3
4. `04-kubernetes-streaming`: Kinesis → EKS/KCL worker → S3
5. `05-cdc`: PostgreSQL/RDS → DMS (or Debezium locally) → S3
6. `06-warehouse`: S3 → Glue/dbt → Redshift
7. `07-realtime-analytics`: Kinesis → Flink → OpenSearch

Every lab contains a README, sample data, application code, Terraform, a Docker path, a Kubernetes manifest or explanation, and verification/cleanup instructions. The root GitHub Actions workflows validate all labs and deploy one selected lab at a time.

## The three modes

“Native”, “Docker”, and “Kubernetes” describe where custom processing code runs. S3, Kinesis, SQS, SNS, DMS, Redshift, and OpenSearch remain managed AWS services.

| Mode | Intended use |
|---|---|
| Native AWS | Lambda, Glue, DMS, Managed Flink, Redshift |
| Docker | Reproducible local runtime or ECS/Fargate |
| Kubernetes | CronJob/Deployment on an existing EKS cluster |

## Safety

Nothing deploys automatically. Use a sandbox account, AWS SSO, `eu-west-1`, a budget alarm, and `terraform plan` before `apply`. EKS, DMS, Redshift, Managed Flink, NAT Gateway, and OpenSearch can incur charges while idle. Destroy each lab after practice.

## Common workflow

```bash
aws sso login --profile data-lab-dev
export AWS_PROFILE=data-lab-dev
export AWS_REGION=eu-west-1

cd labs/01-batch-lake
make test
make local
cd terraform
terraform init
terraform plan
terraform apply
terraform destroy
```

Each lab README supplies the exact variant-specific commands and explains what to inspect in AWS.

