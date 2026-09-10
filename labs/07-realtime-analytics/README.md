# Lab 7: Real-time analytics

Native AWS is Kinesis → Managed Service for Apache Flink → OpenSearch. Docker runs Flink locally. Kubernetes uses the Flink Kubernetes Operator and an ECR image.

Build the shaded JAR with `mvn package`, upload it to an artifact S3 bucket, provide bucket variables, and apply Terraform. Start the Managed Flink application, send JSONL records to Kinesis, inspect Flink/CloudWatch and OpenSearch, then destroy.

The checked-in job intentionally prints normalized events first so ingestion and checkpointing can be verified safely. Completing the OpenSearch sink requires choosing a connector version compatible with the selected Flink runtime and configuring AWS SigV4 authentication. Do that as the final exercise; do not expose OpenSearch publicly.

OpenSearch and Managed Flink are billable while provisioned. Kubernetes requires the Flink operator and workload identity. Docker does not emulate AWS IAM or Managed Flink exactly.
