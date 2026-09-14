# Partner Dataset Data Dictionary

> Design status: This dictionary describes proposed curated datasets. Lab 01 produces evaluation evidence only; target publication is implemented in later ingestion labs.


## Dataset: validated_customers

### Dataset definition

| Item | Value |
|---|---|
| Business description | Validated customer records accepted from the partner delivery |
| Grain | One record per accepted customer |
| Business key | `customer_id` |
| Source | `partner_customers.csv` |
| Format in this lab | JSON Lines |
| Update pattern | Incremental practice delivery |
| Classification | Confidential |
| Owner | To be assigned |
| Retention | To be agreed |

### Fields

| Field | Type | Required | Business definition | Example | Classification |
|---|---|---|---|---|---|
| `customer_id` | string | Yes | Stable identifier assigned to one customer | `c-1001` | Internal identifier |
| `email_address` | string | Yes | Normalized customer email used only for approved purposes | `alice.one@example.com` | Personal data |
| `first_name` | string | No | Customer given name | `Alice` | Personal data |
| `last_name` | string | No | Customer family name | `One` | Personal data |
| `country_code` | string | Yes | Agreed country code associated with the customer | `DK` | Personal data |
| `signup_timestamp_utc` | timestamp | Yes | Time the customer was registered, normalized to UTC | `2026-08-01T09:15:00Z` | Personal data |
| `customer_status` | string | Yes | Current agreed customer lifecycle status | `active` | Internal |
| `marketing_consent` | boolean | Yes | Whether the source reports valid marketing consent | `TRUE` | Sensitive preference |
| `lifetime_value` | decimal(12,2) | Yes | Accumulated monetary value supplied by the source | `125.50` | Confidential commercial data |
| `ingestion_timestamp_utc` | timestamp | Yes | Time the platform accepted the record | `2026-09-14T12:00:00Z` | Operational |
| `source_file` | string | Yes | Name of the delivered source file | `partner_customers.csv` | Operational |
| `ingestion_run_id` | string | Yes | Identifier connecting records to one pipeline execution | `run-20260914-001` | Operational |

### Controlled values

| Field | Allowed values |
|---|---|
| `customer_status` | `active`, `inactive` |
| `marketing_consent` | `TRUE`, `FALSE` |
| `country_code` | Production standard to be agreed |

## Dataset: validated_events

### Dataset definition

| Item | Value |
|---|---|
| Business description | Validated customer activity records accepted from the partner delivery |
| Grain | One record per accepted event |
| Business key | `event_id` |
| Customer relationship | `customer_id` references `validated_customers.customer_id` |
| Source | `partner_events.jsonl` |
| Format in this lab | JSON Lines |
| Update pattern | Incremental practice delivery |
| Classification | Confidential |
| Owner | To be assigned |
| Retention | To be agreed |

### Fields

| Field | Type | Required | Business definition | Example | Classification |
|---|---|---|---|---|---|
| `event_id` | string | Yes | Stable identifier for one activity event | `e-2001` | Internal identifier |
| `customer_id` | string | Yes | Customer associated with the event | `c-1001` | Internal identifier |
| `event_type` | string | Yes | Controlled category describing the activity | `purchase` | Behavioral data |
| `event_timestamp_utc` | timestamp | Yes | Time the activity occurred, normalized to UTC | `2026-08-12T08:15:00Z` | Behavioral data |
| `amount` | decimal(12,2) | Conditional | Monetary value associated with a purchase | `49.95` | Confidential commercial data |
| `event_source` | string | Yes | Channel or system that generated the activity | `web` | Behavioral data |
| `ingestion_timestamp_utc` | timestamp | Yes | Time the platform accepted the event | `2026-09-14T12:00:00Z` | Operational |
| `source_file` | string | Yes | Name of the delivered event file | `partner_events.jsonl` | Operational |
| `source_line_number` | integer | Yes | Physical source line used for traceability | `2` | Operational |
| `ingestion_run_id` | string | Yes | Identifier connecting events to one pipeline execution | `run-20260914-001` | Operational |

### Controlled values

| Field | Allowed values |
|---|---|
| `event_type` | `page_view`, `purchase`, `email_open`, `email_click` |
| `event_source` | `web`, `email`, `store` |

## Dataset: rejected_records

### Dataset definition

| Item | Value |
|---|---|
| Business description | Records that failed one or more validation rules |
| Grain | One record per rejected source record or malformed source line |
| Purpose | Investigation, correction, reconciliation, and controlled replay |
| Classification | Same as or stricter than the source dataset |
| Access | Restricted operational access |
| Retention | To be agreed |

### Fields

| Field | Type | Required | Business definition |
|---|---|---|---|
| `line_number` | integer | Yes | Physical location of the source record |
| `error_codes` | array of strings | Yes | Machine-readable validation failures |
| `record` | object or null | No | Parsed source record when parsing succeeded |
| `ingestion_run_id` | string | Production only | Pipeline execution that rejected the record |

## Relationships

| Parent | Child | Join | Relationship |
|---|---|---|---|
| `validated_customers` | `validated_events` | `customer_id` | One customer to many events |
| Pipeline run | All output datasets | `ingestion_run_id` | One run to many records |

## Quality expectations

| Check | Target |
|---|---|
| Missing business keys | 0% |
| Duplicate business keys | 0% |
| Invalid required timestamps | 0% |
| Negative monetary values | 0% |
| Event-to-customer match rate | At least 99.9% |
| Reconciliation difference | 0 records |
| Unannounced breaking schema changes | 0 |

## Known limitations

- Practice country codes use a small allowlist.
- Email validation does not prove that a mailbox exists.
- Consent legality cannot be inferred from a Boolean value alone.
- Production ownership and retention are intentionally left for approval.
- All examples are synthetic.
