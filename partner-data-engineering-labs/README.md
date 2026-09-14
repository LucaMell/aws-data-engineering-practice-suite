# Partner Data Engineering Lab Series

A practical series for turning external partner data into reliable, reusable,
secure, and well-documented data products.

The labs cover partner evaluation, ingestion, transformation, validation,
orchestration, replication, analytics, secure delivery, and production
operations.

## Lab roadmap

| Lab | Focus | Main tools |
|---|---|---|
| 00 | Delivery baseline and repository standards | Git, GitHub Actions, pytest, Docker, Terraform |
| 01 | Partner dataset evaluation | Python, SQL, DuckDB, Pandas/Polars |
| 02 | Secure file ingestion | S3, IAM, Boto3, Moto, checksums |
| 03 | Lake formats and schema evolution | CSV, JSON, Parquet, ORC, PyArrow, Spark |
| 04 | Catalogue-backed analytics | Glue Data Catalog, Athena, Presto SQL |
| 05 | Distributed ETL | AWS Glue, PySpark, Spark SQL |
| 06 | API and webhook ingestion | Python, FastAPI, HTTP, API Gateway patterns |
| 07 | Data quality and observability | SQL checks, JSON Schema, Pandera, pytest |
| 08 | Airflow orchestration | Airflow, Docker Compose, Postgres |
| 09 | Prefect orchestration | Prefect, Python, Docker |
| 10 | Warehouse modelling | SQL, DuckDB, Postgres, dimensional modelling |
| 11 | Platform portability | Snowflake, Databricks, Redshift, Hive, Presto/Trino |
| 12 | Replication and CDC | Postgres, Debezium, Kafka/Redpanda, DMS patterns |
| 13 | Event-driven and streaming data | SQS, SNS, EventBridge, Lambda, Kinesis, Firehose, ECS |
| 14 | Secure outbound delivery | S3, SFTP, encryption, manifests, orchestration |
| 15 | Security and compliance | IAM, S3 policies, KMS and Secrets Manager patterns |
| 16 | AI-assisted engineering | AI-supported analysis, documentation, code and verification |
| 17 | End-to-end partner-data capstone | All core tools and architectures |

## Architecture coverage

The series includes:

- partner-pushed files and internally pulled files;
- scheduled batch and micro-batch processing;
- API polling and webhook delivery;
- full snapshots and incremental watermarks;
- database replication and log-based CDC;
- work queues, notification fan-out, event routing, and continuous streams;
- ETL and ELT;
- data lake, warehouse, and lakehouse architectures;
- inbound onboarding and secure outbound delivery;
- local, Docker, AWS, and production deployment patterns.

## Working modes

Every relevant lab clearly distinguishes:

1. Local testing — Python, SQL, and tests on the computer.
2. Docker testing — reproducible services and local emulators.
3. AWS testing — small, supervised deployments when the account supports them.
4. Production design — secure and scalable architecture retained for study.

## Safety rules

- Local and Docker tests come before AWS.
- No paid Terraform resource is applied without an explicit warning and approval.
- Blocked or expensive services receive local implementations and validated
  production designs.
- Never paste or commit access keys, passwords, tokens, or real partner data.
- Use dummy local credentials, environment variables, OIDC, and secret
  references.
- Every AWS deployment includes immediate cleanup and post-destroy verification.
- Terraform state, plans, generated data, logs, and secret files remain ignored.

## Standard lab contents

Each completed lab should contain:

- `README.md`
- `src/`
- `sql/`
- `tests/`
- `sample/`
- `schemas/`
- `docs/`
- Docker or Docker Compose configuration where useful
- Terraform where useful
- a `Makefile` with consistent local commands

## Evidence produced by each lab

A completed lab provides:

- working application or pipeline code;
- automated unit and integration tests;
- an architecture explanation;
- source-to-target field mapping;
- data dictionary;
- validation results;
- operational runbook;
- documented trade-offs and failure handling;
- a concise interview-ready project explanation.

## Cost policy

The default path is free and local.

Small AWS tests are optional. Athena queries use tiny datasets and scan limits.
Glue jobs, Kinesis, EKS, DMS, Redshift, Managed Flink, OpenSearch, NAT Gateway,
and continuously running compute remain local or study-only unless separately
reviewed and approved.
