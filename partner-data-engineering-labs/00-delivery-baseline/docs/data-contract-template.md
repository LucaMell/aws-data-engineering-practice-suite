# Partner Data Contract

## Contract metadata

| Item | Value |
|---|---|
| Contract name | |
| Contract version | |
| Status | Draft / approved / deprecated |
| Data producer | |
| Data consumer | |
| Business owner | |
| Technical owner | |
| Effective date | |
| Review date | |

## Purpose

Describe:

- Why the dataset is exchanged.
- Which business processes use it.
- What is outside the scope of this contract.

## Delivery agreement

| Item | Agreed value |
|---|---|
| Delivery method | S3 / SFTP / API / webhook / database / stream |
| Delivery pattern | Full / incremental / CDC |
| Frequency | |
| Expected arrival time | |
| Timezone | |
| Expected volume | |
| Maximum file or message size | |
| Historical backfill | |
| Retention period | |
| Replay support | |
| Compression | |
| Encryption | |

## Naming and location

| Item | Convention |
|---|---|
| Filename | |
| S3 object key or API route | |
| Partition structure | |
| Temporary-file suffix | |
| Completion indicator | |
| Quarantine location | |

## Format rules

| Item | Agreed value |
|---|---|
| Format | CSV / JSON / JSON Lines / Parquet / ORC |
| Character encoding | UTF-8 |
| Delimiter | |
| Header included | |
| Quote character | |
| Escape character | |
| Decimal separator | |
| Date format | |
| Timestamp format | |
| Timestamp timezone | UTC unless agreed otherwise |
| Null representation | |
| Empty-string meaning | |

## Schema

| Field | Type | Required | Nullable | Description | Example | Sensitive |
|---|---|---|---|---|---|---|
| customer_id | string | Yes | No | Stable customer identifier | c-1001 | Internal identifier |
| email | string | Yes | No | Customer email address | user@example.com | Personal data |
| event_timestamp | timestamp | Yes | No | Time the source event occurred | 2026-09-14T12:30:00Z | No |
| | | | | | | |

The detailed business definitions belong in the data dictionary. Transformations belong in the field mapping.

## Business key and duplicate rules

| Rule | Agreement |
|---|---|
| Business key | |
| Uniqueness scope | Per file / per day / global |
| Duplicate detection | |
| Duplicate resolution | |
| Idempotency key | |

## Quality expectations

| Check | Expected result | Warning threshold | Failure threshold |
|---|---|---|---|
| Schema | Matches the agreed version | | Any incompatible change |
| Required fields | Populated | | |
| Uniqueness | Business keys are unique | | |
| Valid values | Values match agreed formats and ranges | | |
| Freshness | Delivery arrives on time | | |
| Reconciliation | Input = accepted + rejected | Any unexplained difference | Any unexplained difference |

## Invalid-data handling

| Failure type | Action |
|---|---|
| Missing delivery | Alert and contact producer |
| Invalid filename | Quarantine delivery |
| Incompatible schema | Reject or quarantine delivery |
| Invalid record | Quarantine record with a reason |
| Duplicate record | Apply the agreed duplicate rule |
| Temporary platform failure | Retry with bounded backoff |
| Permanent processing failure | Stop publication and escalate |

Invalid data must never be silently discarded.

## Schema-change policy

- The producer announces proposed changes before delivery.
- Additive and breaking changes are identified separately.
- New optional fields may be backward compatible after approval.
- Removed, renamed, retyped, or newly required fields are breaking changes.
- Breaking changes require a new contract version and consumer approval.
- Both parties agree on a migration and retirement period.
- Unannounced incompatible changes may be quarantined.

## Service expectations

| Measure | Agreement |
|---|---|
| Availability target | |
| Delivery deadline | |
| Maximum acceptable lateness | |
| Incident acknowledgement | |
| Correction or replay target | |
| Planned-maintenance notice | |

These values are practice targets unless formally approved by the responsible teams.

## Security and compliance

| Requirement | Agreement |
|---|---|
| Data classification | |
| Personal or sensitive fields | |
| Approved purpose | |
| Encryption in transit | |
| Encryption at rest | |
| Access-control method | |
| Permitted accounts or roles | |
| Logging restrictions | |
| Retention and deletion | |
| Data residency | |
| Offboarding procedure | |

Credentials and secrets must never appear in this contract.

## Monitoring and evidence

For every delivery, retain:

- Delivery identifier and arrival time.
- Source, accepted, rejected, and output counts.
- Schema-validation result.
- Data-quality results.
- Pipeline run identifier.
- Publication result.
- Non-sensitive failure reasons.

## Communication and escalation

| Event | Producer action | Consumer action | Contact |
|---|---|---|---|
| Late delivery | Notify consumer | Assess downstream impact | |
| Schema change | Submit proposed version | Review and test | |
| Quality failure | Investigate source | Quarantine and report evidence | |
| Security incident | Escalate immediately | Restrict access and follow incident process | |

## Acceptance criteria

- [ ] Delivery method tested.
- [ ] Schema validated.
- [ ] Field mapping approved.
- [ ] Data dictionary approved.
- [ ] Quality thresholds tested.
- [ ] Reconciliation tested.
- [ ] Invalid-data path tested.
- [ ] Replay tested.
- [ ] Security controls reviewed.
- [ ] Runbook reviewed.
- [ ] Producer and consumer approve the contract.

## Approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Producer owner | | | |
| Consumer owner | | | |
| Data engineer | | | |
| Security or compliance, if required | | | |

## Change history

| Version | Date | Author | Change | Approved by |
|---|---|---|---|---|
| 0.1 | | | Initial draft | |
