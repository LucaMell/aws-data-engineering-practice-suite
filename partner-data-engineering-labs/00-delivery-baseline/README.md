# Lab 00: Delivery Baseline and Repository Standards

## Business scenario

A data engineering team receives feeds from several external partners. Each
pipeline may use different sources and platforms, but all pipelines must follow
the same minimum standards for testing, documentation, security, deployment,
and cleanup.

This lab creates those shared standards before any partner-specific pipeline is
built.

## Learning objectives

By completing this lab, you will be able to:

- distinguish local validation, Docker testing, AWS deployment, and production
  deployment;
- apply consistent repository and documentation standards;
- run Python, SQL, Terraform, and Docker checks in continuous integration;
- explain how GitHub Actions deploys Terraform through AWS OIDC;
- prevent secrets and generated files from entering Git;
- require review before infrastructure changes are applied;
- produce repeatable evidence that a pipeline is safe to release;
- destroy temporary cloud resources and verify that cleanup succeeded.

## Current repository baseline

The repository already has:

- Python tests with pytest;
- Terraform formatting and validation;
- Docker image builds;
- a `Validate suite` GitHub Actions workflow;
- a manually triggered `Deploy selected lab` workflow;
- local Terraform state ignored by Git;
- an AWS sandbox profile named `data-lab-dev`;
- AWS region `eu-west-1`.

The current validation workflow covers the original `labs/` directory. It must
later be extended to include `partner-data-engineering-labs/`.

The deployment workflow must not be used until its AWS OIDC role, GitHub
environment protections, and Terraform state strategy have been reviewed and
configured.

## Delivery flow

```text
Developer change
      |
      v
Local tests and formatting
      |
      v
Docker integration test
      |
      v
Git commit and pull request
      |
      v
GitHub Actions validation
      |
      v
Reviewed Terraform plan
      |
      v
Approved dev deployment
      |
      v
Runtime and data verification
      |
      v
Cleanup or controlled promotion
```

## The four execution modes

### 1. Local testing

Runs directly on the computer.

Examples:

- Python unit tests;
- SQL tests using DuckDB;
- schema and data-quality checks;
- Terraform formatting and validation.

Local testing must not require AWS credentials.

### 2. Docker testing

Runs applications and dependencies in isolated local containers.

Examples:

- Moto or LocalStack for AWS-compatible APIs;
- Postgres for source and warehouse tests;
- Airflow, Prefect, Trino, Hive, Kafka, or Redpanda;
- API and SFTP partner simulators.

Docker testing must use synthetic data and dummy credentials.

### 3. AWS development deployment

Creates temporary resources in the sandbox AWS account.

Requirements:

- inspect the exact Terraform plan;
- provide a cost warning;
- receive explicit approval;
- deploy only one lab;
- test valid and invalid paths;
- destroy temporary resources immediately unless continued operation was
  explicitly approved;
- verify that no billable tasks or resources remain.

### 4. Production deployment

Represents how a real organization should release the solution.

Production principles:

- separate accounts or environments;
- remote encrypted Terraform state and locking;
- least-privilege OIDC deployment roles;
- protected GitHub environments and required reviewers;
- immutable artifacts promoted from development;
- private networking where appropriate;
- monitoring, alerting, audit trails, rollback, and documented ownership.

The practice suite documents production deployment but does not treat the
sandbox account as production.

## Required checks

Every lab should eventually support the relevant subset of these commands:

```bash
python -m pytest -q
python -m compileall -q .
terraform fmt -check -recursive .
terraform validate
docker build .
docker compose config
```

A green command alone is not enough. Integration labs must also verify:

- valid data reaches the expected destination;
- invalid data reaches quarantine or a dead-letter path;
- record counts reconcile;
- reruns do not create incorrect duplicates;
- retriable failures remain retriable;
- logs contain identifiers but not secrets or raw personal data;
- cleanup removes temporary cloud resources.

## Git and secret rules

Never commit:

- AWS access keys;
- GitHub tokens;
- API tokens;
- passwords;
- private keys;
- Terraform state or plans;
- `.env` files;
- real partner or customer data;
- generated outputs and runtime logs.

Commit safe examples such as `.env.example` containing variable names without
secret values.

Use:

- AWS OIDC for GitHub Actions;
- AWS SSO or the configured local profile for supervised development;
- environment variables or secret references at runtime;
- synthetic test data.

## Documentation required for each pipeline

Each partner pipeline should include:

- business purpose;
- source and delivery method;
- architecture and data flow;
- source-to-target field mapping;
- data dictionary;
- data contract and schema;
- validation and reconciliation rules;
- schedule and freshness expectation;
- retry and replay behaviour;
- security and PII classification;
- monitoring and alerting;
- operational runbook;
- ownership and escalation path;
- cost and cleanup notes.

## Lab deliverables

This lab will add:

1. A generic partner-pipeline checklist.
2. A source-to-target mapping template.
3. A data dictionary template.
4. An operational runbook template.
5. A data-contract template.
6. A pull-request checklist.
7. Validation coverage for the new lab directory.
8. A reviewed OIDC deployment design.
9. A safe plan-before-apply deployment process.

## Definition of done

Lab 00 is complete when:

- the generic templates exist;
- automated tests discover both the original and partner-focused labs;
- CI validates Python and Terraform in both locations;
- Docker validation is added only for labs that actually contain Dockerfiles;
- no automatic AWS deployment occurs on push or pull request;
- the manual deployment workflow cannot silently deploy unreviewed production
  infrastructure;
- OIDC requirements are documented;
- the repository is clean and GitHub validation passes.

## Cost and safety

This lab creates no AWS resources.

OIDC configuration and deployment testing will be handled separately. No
deployment workflow will run until its permissions and target resources have
been inspected and explicitly approved.
