# Lab 3: Container streaming on ECS/Fargate

## Goal

Learn how a long-running container consumes streaming records.

The worker:

1. Polls a one-shard Kinesis stream.
2. Normalizes valid email addresses.
3. Writes valid events to S3.
4. Sends invalid events to quarantine SQS.
5. Publishes invalid-event alerts to SNS.
6. Stops gracefully when the container receives `SIGTERM`.

## Architecture

```text
Kinesis -> long-running Docker worker -> S3
                                   \-> quarantine SQS
                                   \-> SNS alerts
```

The one-shard/one-worker constraint is intentional. The worker does not
coordinate multiple consumers or save checkpoints. Lab 4 introduces KCL for
checkpointing and horizontal scaling.

Because the iterator uses `TRIM_HORIZON`, restarting the worker rereads retained
records. The fixed S3 object key makes valid output partly idempotent, but
invalid records can generate repeated quarantine messages and alerts.

## How this differs from Lab 2

Lab 2 uses Lambda: AWS starts short-lived code when an event arrives.

Lab 3 uses a container: the process stays alive, polls continuously, handles
shutdown signals, and owns more of its runtime lifecycle.

## Local unit test

```bash
python -m pytest -q labs/03-container-streaming/test_worker.py
```

The unit tests use in-memory fake AWS clients and cannot contact AWS.

## Local Docker test

Build the worker locally:

```bash
docker build \
  -t lab3-container-stream:local \
  labs/03-container-streaming
```

The worker supports `AWS_ENDPOINT_URL`, allowing all four AWS clients to use a
free local emulator such as Moto.

The validated local setup used:

- Moto at `http://lab3-moto:5000`
- one simulated Kinesis shard
- one simulated S3 bucket
- one quarantine SQS queue
- one SQS queue subscribed to the simulated SNS topic
- fake credentials named `testing`

Both paths were verified:

- valid Kinesis record -> normalized JSON in simulated S3
- invalid Kinesis record -> simulated quarantine SQS and SNS subscriber

No real AWS credentials or resources are required for the local test.

## Terraform

The Terraform configuration demonstrates the native AWS architecture:

- Kinesis
- ECS Fargate
- S3
- SQS
- SNS
- IAM
- CloudWatch Logs

It is retained for study and validation only.

Do not run `terraform apply` for this lab on the AWS Free plan. Kinesis and
Fargate can create ongoing charges. Production networking should also use
private subnets and VPC endpoints instead of a public IP in the default VPC.

Safe validation:

```bash
terraform -chdir=labs/03-container-streaming/terraform validate
```

The Kubernetes manifest shows how the same image could run on EKS, but it is
illustrative and is not a complete deployment.
