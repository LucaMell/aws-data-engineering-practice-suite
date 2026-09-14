# Data Dictionary

## Dataset overview

| Item | Value |
|---|---|
| Dataset name | |
| Business description | |
| Business owner | |
| Technical owner | |
| Source system | |
| Storage location | |
| Format | CSV / JSON / Parquet / ORC / table |
| Update frequency | |
| Retention period | |
| Data classification | Public / internal / confidential / restricted |
| Version | |

## Dataset grain

Describe exactly what one record represents.

## Business keys

| Key | Fields | Expected uniqueness |
|---|---|---|
| Primary business key | | |
| Secondary key | | |

## Fields

| Field | Business definition | Type | Required | Nullable | Example | Allowed values | Classification | Source |
|---|---|---|---|---|---|---|---|---|
| customer_id | Stable customer identifier | string | Yes | No | c-1001 | Non-empty | Internal | Source |
| email_address | Normalized email address | string | Yes | No | user@example.com | Valid email | Personal data | Source |
| amount | Monetary order value | decimal(12,2) | Yes | No | 99.95 | At least zero | Internal | Derived |
| event_timestamp | Source event time in UTC | timestamp | Yes | No | 2026-09-14T12:30:00Z | ISO 8601 | Internal | Source |
| ingestion_timestamp | Time the pipeline accepted the record | timestamp | Yes | No | 2026-09-14T12:31:05Z | ISO 8601 | Operational | Pipeline |
| | | | | | | | | |

## Relationships

| Field | Related dataset | Related field | Relationship |
|---|---|---|---|
| customer_id | customers | customer_id | Many-to-one |
| | | | |

## Physical layout

| Item | Value |
|---|---|
| Partition fields | |
| Object-key convention | |
| Compression | |
| Target file size | |
| Sort or clustering fields | |

## Quality expectations

| Check | Scope | Expected result | Failure action |
|---|---|---|---|
| Required values | Business key | 100% populated | Quarantine |
| Uniqueness | Business key | Unique | Deduplicate or fail |
| Valid format | Relevant fields | Contract-compliant | Quarantine |
| Freshness | Dataset | Delivered on time | Alert |
| Reconciliation | Delivery | Input = accepted + rejected | Stop publication |

## Known limitations

| Limitation | Impact | Workaround | Owner |
|---|---|---|---|
| | | | |

## Approved and restricted uses

Document which uses are approved and which are prohibited.

## Change history

| Version | Date | Author | Change | Approved by |
|---|---|---|---|---|
| 0.1 | | | Initial draft | |
