# Pipeline Operations Runbook

## Pipeline summary

| Item | Value |
|---|---|
| Pipeline name | |
| Business purpose | |
| Business owner | |
| Technical owner | |
| Source | |
| Destination | |
| Schedule or trigger | |
| Expected completion time | |
| Repository | |
| Logs | |
| Dashboard | |
| Alert destination | |
| Last reviewed | |

## Data flow

Describe the stages from source delivery to final publication.

1. Receive the source data.
2. Preserve the raw delivery when permitted.
3. Validate the file, schema, and records.
4. Quarantine invalid data.
5. Transform accepted records.
6. Publish the result.
7. Reconcile counts and report quality results.

## Dependencies

| Dependency | Purpose | Owner | Failure impact |
|---|---|---|---|
| Source delivery | Supplies data | | |
| Storage | Holds raw and processed data | | |
| Processing service | Validates and transforms data | | |
| Catalog or database | Makes data queryable | | |
| Notification service | Sends alerts | | |

## Normal operating checks

- [ ] The expected delivery arrived.
- [ ] The pipeline started and completed on time.
- [ ] Input, accepted, rejected, and output counts reconcile.
- [ ] Data-quality checks passed.
- [ ] Expected files, partitions, or tables were created.
- [ ] No unexpected schema change occurred.
- [ ] Runtime and cost remain within their expected ranges.

## Expected metrics

| Metric | Expected | Warning threshold | Failure threshold |
|---|---|---|---|
| Input records | | | |
| Rejected records | | | |
| Duplicate rate | | | |
| Null rate | | | |
| Data freshness | | | |
| Processing duration | | | |
| Output records | | | |

## Alert response

1. Record the pipeline name, run ID, and alert time.
2. Check whether the source delivery arrived.
3. Inspect logs without copying secrets or personal data.
4. Classify the problem as data, code, permission, infrastructure, or partner-related.
5. Confirm whether retrying is safe and idempotent.
6. Escalate to the correct owner.
7. Record the action and result.

## Common incidents

| Symptom | Investigation | Safe response |
|---|---|---|
| No delivery | Check schedule and source location | Contact the source owner |
| Schema mismatch | Compare delivery with the data contract | Quarantine and request clarification |
| Count mismatch | Compare counts at every stage | Stop publication until reconciled |
| Access denied | Identify the denied action and resource | Restore only the required permission |
| Timeout | Check volume, runtime, and logs | Retry only after checking idempotency |
| High rejection rate | Group failures by reason | Notify the owner using non-sensitive examples |
| Destination unavailable | Check service and connection status | Retry with backoff or pause safely |

## Retry procedure

- Confirm the error is retriable.
- Confirm a retry cannot create harmful duplicates.
- Record the failed run ID.
- Retry only the failed unit when possible.
- Run reconciliation and quality checks again.
- Record the new run ID and result.

## Replay or backfill procedure

1. Confirm the date range and business reason.
2. Confirm the original source data still exists.
3. Obtain approval from the data owner.
4. Assign a unique replay identifier.
5. Test the replay locally or in development.
6. Process the smallest required range.
7. Verify idempotency and record counts.
8. Confirm downstream output is correct.
9. Save completion evidence.

## Rollback or correction

Document:

- What can be rolled back.
- What data may already have been published.
- Whether corrected data replaces or supplements previous data.
- How downstream users are notified.
- How the corrected result is verified.

## Quarantine handling

- Preserve the record or a safe reference to it.
- Store a machine-readable rejection reason.
- Restrict access to sensitive records.
- Replay corrected records through an approved process.
- Never silently discard invalid records.

## Security rules

- Never store credentials or tokens in this document.
- Never paste sensitive payloads into tickets or chat.
- Use least-privilege access.
- Log identifiers rather than complete personal records.
- Escalate suspected exposure immediately.

## Cost controls

- Monitor storage growth and retention.
- Monitor query scan sizes.
- Stop short-lived compute after testing.
- Destroy temporary practice resources.
- Obtain approval before increasing paid capacity.

## Cleanup order

1. Stop producers or scheduled triggers.
2. Stop processing safely.
3. Preserve required logs and evidence.
4. Remove temporary data.
5. Destroy infrastructure from its original Terraform state.
6. Confirm that no temporary resources remain.

## Contacts and escalation

| Situation | Owner | Communication method |
|---|---|---|
| Source delivery problem | | |
| Pipeline failure | | |
| Data-quality problem | | |
| Security concern | | |
| Business-impact decision | | |

## Incident record

| Item | Value |
|---|---|
| Incident ID | |
| Start and end time | |
| Impact | |
| Root cause | |
| Resolution | |
| Preventive action | |
| Owner | |

## Change history

| Version | Date | Author | Change | Approved by |
|---|---|---|---|---|
| 0.1 | | | Initial draft | |
