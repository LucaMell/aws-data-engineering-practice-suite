# Partner Dataset Evaluation Report

## Executive decision

**Recommendation: Proceed with conditions**

The sample demonstrates useful customer and activity data, stable candidate identifiers, and joinable datasets. However, the delivery is not ready for automated production ingestion without validation, quarantine, schema controls, and corrections from the data producer.

## Evaluation scope

| Item | Value |
|---|---|
| Customer source | `sample/partner_customers.csv` |
| Event source | `sample/partner_events.jsonl` |
| Evaluation method | Python profiling and DuckDB SQL |
| Data type | Synthetic practice data |
| Customer format | CSV |
| Event format | JSON Lines |
| Evaluation environment | Local workstation |
| AWS services used | None |

## Structure

### Customers

- 12 records excluding the header.
- 9 source columns.
- Candidate business key: `customer_id`.
- Sensitive fields include name and email.
- Customer timestamps are expected in ISO 8601 UTC format.

### Events

- 13 physical input lines.
- 12 parseable JSON objects.
- 1 malformed JSON line.
- Candidate business key: `event_id`.
- `customer_id` provides the relationship to customers.
- Event timestamps are expected in ISO 8601 UTC format.

## Processing results

| Dataset | Input | Accepted | Rejected | Reconciles |
|---|---:|---:|---:|---|
| Customers | 12 | 4 | 8 | Yes |
| Events | 13 | 5 | 8 | Yes |

For both datasets:

`input = accepted + rejected`

No record is silently discarded.

## Customer findings

| Rejection reason | Count |
|---|---:|
| Duplicate customer ID | 1 |
| Invalid country code | 1 |
| Invalid email | 2 |
| Invalid marketing-consent value | 1 |
| Invalid signup timestamp | 1 |
| Invalid status | 1 |
| Missing customer ID | 1 |
| Negative lifetime value | 1 |

Eight customer records were rejected. One record can have more than one rejection reason, so rejection-reason totals may be higher than rejected-record totals.

Observed normalization:

- Email addresses are trimmed.
- Email addresses are converted to lowercase.
- Status and consent values are normalized to lowercase.
- Valid lifetime values are converted to numbers.

## Event findings

| Rejection reason | Count |
|---|---:|
| Duplicate event ID | 1 |
| Invalid event source | 1 |
| Invalid event timestamp | 1 |
| Invalid event type | 1 |
| Invalid purchase amount | 1 |
| Malformed JSON | 1 |
| Missing event customer ID | 1 |
| Missing event ID | 1 |
| Customer not found in accepted customers | 3 |

Eight event lines were rejected. Some rejected events have several reasons.

The malformed JSON line was quarantined without stopping processing of the other lines.

## Coverage findings

| Measure | Result |
|---|---:|
| Accepted customers | 4 |
| Accepted customers with activity | 4 |
| Accepted-customer activity coverage | 100.00% |
| Non-empty event customer references matching accepted customers | 72.73% |

The activity coverage is encouraging, but the event-to-customer match rate is below a reasonable production threshold. The producer and consumer must agree on how orphan events are corrected, delayed, or rejected.

## Usability assessment

### Strengths

- Customers and events have candidate business keys.
- The two datasets can be joined through `customer_id`.
- Accepted records contain parseable timestamps.
- Event types provide useful behavioral categories.
- Purchase events contain an amount field.
- Data can be processed incrementally as separate records.

### Risks

- Duplicate identifiers could cause double processing.
- Invalid or missing identifiers prevent reliable joins.
- Uncontrolled status, consent, event-type, and source values create ambiguity.
- Invalid timestamps prevent correct ordering and incremental processing.
- Invalid monetary values can corrupt reporting.
- Malformed JSON requires line-level isolation.
- Personal and behavioral data requires controlled access and safe logging.

## Conditions before onboarding

1. Approve a versioned data contract.
2. Agree required fields and controlled values.
3. Require unique `customer_id` and `event_id` values.
4. Require ISO 8601 timestamps with an agreed timezone.
5. Define the meaning and legal source of marketing consent.
6. Agree country-code standards.
7. Reject negative lifetime and purchase values.
8. Define orphan-event handling.
9. Implement idempotent ingestion and replay.
10. Preserve rejected records with machine-readable reasons.
11. Reconcile every delivery.
12. Define retention, encryption, IAM, and logging rules.
13. Agree how schema changes and corrections are communicated.

## Proposed acceptance thresholds

These are practice thresholds and require owner approval before production use.

| Measure | Proposed threshold |
|---|---|
| Missing business key | 0% |
| Duplicate business key | 0% |
| Malformed records | 0% |
| Invalid required timestamp | 0% |
| Event-to-customer match rate | At least 99.9% |
| Reconciliation difference | 0 records |
| Unannounced breaking schema changes | 0 |
| Late delivery | Within agreed service expectation |

## Evidence produced

The evaluator creates:

- `output/profile.json`
- `output/accepted_customers.jsonl`
- `output/rejected_customers.jsonl`
- `output/accepted_events.jsonl`
- `output/rejected_events.jsonl`
- `output/sql_summary.json`
- Five CSV reports under `output/sql/`

The `output/` directory is generated evidence and is intentionally excluded from Git.

## Limitations

- The sample is deliberately small and synthetic.
- Email validation checks structure, not mailbox ownership.
- Country validation uses a small practice allowlist.
- The evaluation does not establish legal permission to use the data.
- Production thresholds require agreement from responsible owners.
- No AWS service or production environment was tested in this stage.

## Final recommendation

Proceed to a controlled development ingestion only after the conditions above are captured in an approved contract and implemented as automated checks. Do not publish the current rejected records to downstream consumers.
