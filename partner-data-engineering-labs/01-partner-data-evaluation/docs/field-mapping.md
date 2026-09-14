# Partner Dataset Field Mapping

> Design status: This is the proposed target mapping for a future ingestion pipeline. Lab 01 evaluates and separates source records but does not publish these target tables.


## Integration details

| Item | Value |
|---|---|
| Integration | Synthetic partner customer and activity feed |
| Customer source | `partner_customers.csv` |
| Event source | `partner_events.jsonl` |
| Customer target | `validated_customers` |
| Event target | `validated_events` |
| Delivery pattern | Incremental file delivery |
| Mapping version | 1.0 |
| Status | Draft for review |

## Customer mappings

| Source field | Target field | Target type | Required | Transformation | Validation | Classification |
|---|---|---|---|---|---|---|
| `customer_id` | `customer_id` | string | Yes | Trim whitespace | Non-empty and unique per delivery | Internal identifier |
| `email` | `email_address` | string | Yes | Trim and lowercase | Basic email structure | Personal data |
| `first_name` | `first_name` | string | No | Trim whitespace | None | Personal data |
| `last_name` | `last_name` | string | No | Trim whitespace | None | Personal data |
| `country_code` | `country_code` | string | Yes | Trim and uppercase | Approved ISO-style country allowlist | Personal data |
| `signup_timestamp` | `signup_timestamp_utc` | timestamp | Yes | Parse ISO 8601 and normalize to UTC | Must be parseable | Personal data |
| `status` | `customer_status` | string | Yes | Trim and lowercase | `active` or `inactive` | Internal |
| `marketing_consent` | `marketing_consent` | boolean | Yes | Map `true` and `false` strings to Boolean | Must be an approved value | Sensitive preference |
| `lifetime_value` | `lifetime_value` | decimal(12,2) | Yes | Parse as decimal | Must be at least zero | Confidential commercial data |
| Generated | `ingestion_timestamp_utc` | timestamp | Yes | Set by pipeline | Valid UTC timestamp | Operational metadata |
| Generated | `source_file` | string | Yes | Capture input filename | Non-empty | Operational metadata |
| Generated | `ingestion_run_id` | string | Yes | Capture pipeline run identifier | Non-empty | Operational metadata |

## Event mappings

| Source field | Target field | Target type | Required | Transformation | Validation | Classification |
|---|---|---|---|---|---|---|
| `event_id` | `event_id` | string | Yes | Trim whitespace | Non-empty and unique per delivery | Internal identifier |
| `customer_id` | `customer_id` | string | Yes | Trim whitespace | Must match an accepted customer | Internal identifier |
| `event_type` | `event_type` | string | Yes | Trim and lowercase | `page_view`, `purchase`, `email_open`, or `email_click` | Behavioral data |
| `event_timestamp` | `event_timestamp_utc` | timestamp | Yes | Parse ISO 8601 and normalize to UTC | Must be parseable | Behavioral data |
| `amount` | `amount` | decimal(12,2) | Conditional | Parse as decimal | Purchase amount must be numeric and non-negative | Confidential commercial data |
| `source` | `event_source` | string | Yes | Trim and lowercase | `web`, `email`, or `store` | Behavioral data |
| Generated | `ingestion_timestamp_utc` | timestamp | Yes | Set by pipeline | Valid UTC timestamp | Operational metadata |
| Generated | `source_file` | string | Yes | Capture input filename | Non-empty | Operational metadata |
| Generated | `source_line_number` | integer | Yes | Capture physical line number | Positive integer | Operational metadata |
| Generated | `ingestion_run_id` | string | Yes | Capture pipeline run identifier | Non-empty | Operational metadata |

## Controlled-value mappings

### Customer status

| Source value | Target value | Unknown-value action |
|---|---|---|
| `active` | `active` | Not applicable |
| `inactive` | `inactive` | Not applicable |
| Any other value | None | Quarantine record |

### Marketing consent

| Source value | Target value | Unknown-value action |
|---|---|---|
| `true` | `TRUE` | Not applicable |
| `false` | `FALSE` | Not applicable |
| Any other value | None | Quarantine record |

### Event type

| Source value | Target value | Unknown-value action |
|---|---|---|
| `page_view` | `page_view` | Not applicable |
| `purchase` | `purchase` | Not applicable |
| `email_open` | `email_open` | Not applicable |
| `email_click` | `email_click` | Not applicable |
| Any other value | None | Quarantine record |

## Record rules

| Rule ID | Dataset | Rule | Failure action |
|---|---|---|---|
| C001 | Customers | `customer_id` is required | Quarantine |
| C002 | Customers | `customer_id` is unique per delivery | Quarantine later duplicate |
| C003 | Customers | Email must pass structural validation | Quarantine |
| C004 | Customers | Signup timestamp must be valid | Quarantine |
| C005 | Customers | Lifetime value cannot be negative | Quarantine |
| E001 | Events | Each physical line must be valid JSON | Quarantine line |
| E002 | Events | `event_id` is required and unique | Quarantine |
| E003 | Events | `customer_id` must match an accepted customer | Quarantine |
| E004 | Events | Event timestamp must be valid | Quarantine |
| E005 | Events | Purchase amount must be numeric and non-negative | Quarantine |

## Reconciliation

| Dataset | Required relationship |
|---|---|
| Customers | Input records = accepted customer records + rejected customer records |
| Events | Physical input lines = accepted event records + rejected event records |

## Open production decisions

- Confirm the authoritative country-code standard.
- Confirm whether uniqueness applies per file or globally.
- Confirm whether corrected records replace or supplement earlier records.
- Confirm the legal source and timestamp of consent.
- Confirm whether names are necessary for the approved use.
- Confirm retention periods for raw and rejected data.
- Confirm whether orphan events should be delayed for a later customer delivery.
