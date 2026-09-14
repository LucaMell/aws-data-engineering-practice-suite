# Partner Pipeline Delivery Checklist

## Business and ownership

- [ ] Define the business purpose.
- [ ] Identify the source, business, and technical owners.
- [ ] Record the partner technical contact.
- [ ] Agree the delivery schedule and service expectations.
- [ ] Define escalation and change-communication channels.

## Source and delivery

- [ ] Identify file, API, webhook, database, or stream delivery.
- [ ] Identify full, incremental, or CDC delivery.
- [ ] Record frequency, volume, and maximum size.
- [ ] Define filename, object-key, or API conventions.
- [ ] Define historical backfill and replay requirements.
- [ ] Define duplicate and late-arrival handling.

## Data contract and formats

- [ ] Document required and optional fields.
- [ ] Document types, business keys, nulls, and controlled values.
- [ ] Document timestamps and timezones.
- [ ] Confirm CSV, JSON, Parquet, ORC, or other format rules.
- [ ] Confirm delimiter, quoting, encoding, and compression.
- [ ] Define backward-compatible and breaking schema changes.

## Security and compliance

- [ ] Classify the dataset and sensitive fields.
- [ ] Record approved and prohibited uses.
- [ ] Encrypt data in transit and at rest.
- [ ] Use least-privilege IAM permissions.
- [ ] Keep secrets outside Git.
- [ ] Exclude sensitive payloads from logs.
- [ ] Document retention, deletion, and offboarding.

## Ingestion and transformation

- [ ] Preserve a raw copy when permitted.
- [ ] Separate raw, validated, quarantined, and curated data.
- [ ] Capture delivery time, source identifier, and run ID.
- [ ] Make processing idempotent.
- [ ] Document source-to-target transformations.
- [ ] Define normalization and deduplication rules.
- [ ] Preserve lineage from output to source.
- [ ] Never silently discard invalid records.

## Validation and reconciliation

- [ ] Validate schema, required values, formats, and ranges.
- [ ] Check uniqueness and referential integrity where required.
- [ ] Check null, duplicate, and rejection rates.
- [ ] Check freshness and delivery lateness.
- [ ] Reconcile input = accepted + rejected.
- [ ] Reconcile financial or other important totals.
- [ ] Save validation evidence for every run.

## Testing

- [ ] Add valid, invalid, duplicate, late, and empty samples.
- [ ] Add unit tests for transformation rules.
- [ ] Test locally without contacting AWS.
- [ ] Test the packaged application in Docker where relevant.
- [ ] Test integrations only in an isolated development environment.
- [ ] Test retries, replay, and idempotency.
- [ ] Test permission and failure paths.
- [ ] Use only synthetic or approved test data.

## Operations

- [ ] Define dependencies, retries, timeouts, and concurrency.
- [ ] Define logs, metrics, dashboards, and alerts.
- [ ] Alert on failure, lateness, volume, and quality problems.
- [ ] Create a runbook and recovery procedure.
- [ ] Assign incident ownership and escalation.
- [ ] Test cleanup and disaster-recovery steps.

## Cost controls

- [ ] Estimate storage, scan, compute, request, and transfer costs.
- [ ] Use partitioning and columnar formats where appropriate.
- [ ] Configure lifecycle and retention rules.
- [ ] Configure auto-suspend or scale-to-zero where supported.
- [ ] Set budgets before AWS deployment.
- [ ] Obtain explicit approval before deploying paid practice services.
- [ ] Destroy short-lived resources after testing.

## Documentation and handover

- [ ] Publish the data contract.
- [ ] Publish the field mapping.
- [ ] Publish the data dictionary.
- [ ] Publish the architecture and data-flow summary.
- [ ] Publish deployment, rollback, and runbook instructions.
- [ ] Record assumptions and known limitations.
- [ ] Record acceptance-test evidence.
- [ ] Confirm the final owner and review date.

## Production readiness

- [ ] Separate development and production resources.
- [ ] Inspect the Terraform plan before applying it.
- [ ] Ensure CI validation does not deploy infrastructure.
- [ ] Use short-lived deployment identity such as GitHub OIDC.
- [ ] Require approval for production deployment.
- [ ] Test monitoring, rollback, recovery, and replay.
