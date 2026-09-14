# Source-to-Target Field Mapping

## Integration details

| Item | Value |
|---|---|
| Integration name | |
| Business purpose | |
| Source system | |
| Source owner | |
| Target system | |
| Target owner | |
| Delivery method | File / API / webhook / database / stream |
| Delivery frequency | |
| Mapping version | |
| Approval status | Draft / approved / retired |
| Last updated | |

## Field mappings

| # | Source field | Source type | Required | Target field | Target type | Transformation | Default | Validation | Sensitive |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | customer_id | string | Yes | customer_id | string | Trim whitespace | None | Must not be empty | No |
| 2 | email | string | Yes | email_address | string | Trim and lowercase | None | Must contain `@` | Yes |
| 3 | order_total | decimal | Yes | amount | decimal(12,2) | Round to two decimals | 0.00 | Must be non-negative | No |
| 4 | created_at | string | Yes | event_timestamp | timestamp | Parse and convert to UTC | None | Valid ISO 8601 | No |
| 5 | | | | | | | | | |

## Record-level rules

| Rule ID | Rule | Failure action |
|---|---|---|
| R001 | Every record must contain its business key. | Quarantine |
| R002 | Resolve duplicate keys using the documented ordering rule. | Deduplicate and report |
| R003 | Unexpected fields cannot replace mapped fields. | Report schema difference |
| R004 | Invalid records cannot be silently discarded. | Store rejection reason |

## Enumerated-value mappings

| Source field | Source value | Target value | Unknown-value action |
|---|---|---|---|
| status | active | ACTIVE | Quarantine or review |
| status | inactive | INACTIVE | Quarantine or review |
| | | | |

## Lookup and join rules

| Rule ID | Input field | Reference dataset | Join condition | Join type | Missing-match action |
|---|---|---|---|---|---|
| J001 | | | | | |

## Null and default rules

| Field | Empty-string handling | Null handling | Default | Reason |
|---|---|---|---|---|
| | | | | |

## Rejection categories

| Code | Meaning | Destination |
|---|---|---|
| MISSING_REQUIRED_FIELD | A required value is absent | Quarantine |
| INVALID_FORMAT | A value cannot be parsed | Quarantine |
| UNKNOWN_ENUM_VALUE | A controlled value has no mapping | Quarantine or review |
| DUPLICATE_RECORD | A business key is repeated | Deduplicate and report |
| SCHEMA_MISMATCH | The delivery differs from the contract | Reject or quarantine |

## Reconciliation rules

| Measure | Expected relationship |
|---|---|
| Source records | Accepted records + rejected records |
| Accepted records | Inserted + updated + accepted duplicates |
| Important totals | Source total equals curated total after documented exclusions |
| Distinct business keys | Match after documented deduplication |

## Assumptions and questions

| ID | Assumption or question | Owner | Due date | Status |
|---|---|---|---|---|
| A001 | | | | Open |

## Approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Source owner | | | |
| Data engineer | | | |
| Target owner | | | |
| Security or compliance, if required | | | |

## Change history

| Version | Date | Author | Change | Approved by |
|---|---|---|---|---|
| 0.1 | | | Initial draft | |
