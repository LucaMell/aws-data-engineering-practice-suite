# Architecture map

| Lab | Source | Transport | Processing | Storage/serving | Failure/operations |
|---|---|---|---|---|---|
| 1 Batch lake | CSV partner file | S3 | Glue Spark / Docker / K8s CronJob | Parquet S3, Catalog, Athena | Glue/CloudWatch |
| 2 Serverless stream | JSON events | Kinesis | Lambda ZIP or image | S3 | SQS quarantine, SNS, CloudWatch |
| 3 Container stream | JSON events | Kinesis | ECS/Fargate container | S3 | SQS, SNS, CloudWatch |
| 4 Kubernetes stream | JSON events | Kinesis | KCL pods on EKS | S3 | KCL checkpoints, SQS, SNS |
| 5 CDC | PostgreSQL WAL | DMS / Debezium+Kafka | CDC replication | Parquet S3 / Kafka | DMS validation, offsets |
| 6 Warehouse | CSV in S3 | COPY | dbt/SQL | Redshift Serverless | dbt tests, query logs |
| 7 Real-time analytics | JSON events | Kinesis | Flink | OpenSearch | checkpoints, CloudWatch |

Use Lab 1 for scheduled external feeds like the files you currently validate before loading into Responsys. Use Labs 2–4 to understand the same stream-processing problem across managed serverless, ECS, and EKS. Labs 5–7 introduce stateful infrastructure and should come later because they cost more and require more operational decisions.
