# Lab 01: Partner Data Evaluation

## Business scenario

A potential data partner has supplied two unfamiliar extracts:

- A delimited customer file.
- A JSON Lines activity file.

Before building an ingestion pipeline, you must determine whether the data is structurally valid, useful, sufficiently complete, and safe to onboard.

The result must be understandable to technical teams, business owners, compliance reviewers, and the external data partner.

## Learning objectives

By completing this lab, you will practise:

- Inspecting unfamiliar structured and semi-structured data.
- Profiling schemas, types, counts, nulls, and distinct values.
- Measuring duplicate, validity, and referential-coverage rates.
- Using Python for repeatable data investigation.
- Using SQL for validation and reconciliation.
- Identifying sensitive fields.
- Producing a concise evaluation report.
- Creating field mappings and data-dictionary entries.
- Separating observations, assumptions, risks, and recommendations.
- Using synthetic data instead of real personal data.

## Local architecture

1. Synthetic partner CSV and JSON Lines files arrive in `sample/`.
2. Python reads and profiles both datasets.
3. DuckDB runs SQL validation and reconciliation queries.
4. Invalid records are classified by reason.
5. Results are written to the ignored `output/` directory.
6. A Markdown evaluation report summarizes whether onboarding should proceed.

## Planned files

| File | Purpose |
|---|---|
| `sample/partner_customers.csv` | Synthetic delimited customer delivery |
| `sample/partner_events.jsonl` | Synthetic semi-structured activity delivery |
| `evaluate.py` | Reusable Python profiling and validation |
| `quality.sql` | SQL quality and reconciliation checks |
| `tests/test_evaluate.py` | Automated behavior tests |
| `Dockerfile` | Reproducible local runtime |
| `docs/evaluation-report.md` | Completed technical and business report |
| `docs/field-mapping.md` | Completed source-to-target mapping |
| `docs/data-dictionary.md` | Completed dataset definitions |
| `output/` | Generated reports and rejected records; not committed |

## Evaluation dimensions

### Structure

Determine:

- Which files and datasets were delivered.
- Which fields exist.
- Which data types are observed.
- Whether the structure matches its declared schema.
- Whether rows or JSON objects are malformed.
- Whether schema differences exist between records.

### Usability

Determine:

- Whether identifiers are stable.
- Whether timestamps can be parsed.
- Whether controlled values are understandable.
- Whether records can be joined across datasets.
- Whether the dataset supports the proposed business purpose.

### Coverage

Measure:

- Distinct customers.
- Distinct events.
- Date range.
- Countries represented.
- Customers with activity.
- Events that match a known customer.
- Important segment or category coverage.

### Completeness

Measure:

- Null and empty-value rates.
- Missing required fields.
- Missing business keys.
- Missing timestamps.
- Missing values by country or record type.

### Quality

Measure:

- Duplicate business keys.
- Invalid email formats.
- Invalid timestamps.
- Invalid numeric values.
- Unknown controlled values.
- Orphan events.
- Input, accepted, and rejected record counts.

## Required outputs

The generated evaluation must include:

- File-level record counts.
- Observed columns and types.
- Null counts and percentages.
- Distinct-value counts.
- Minimum and maximum timestamps.
- Duplicate-key counts.
- Validation failures grouped by reason.
- Cross-dataset match rate.
- Accepted and rejected counts.
- A clear recommendation: proceed, proceed with conditions, or stop.

## Decision rules

Use evidence rather than intuition.

| Decision | Meaning |
|---|---|
| Proceed | Data meets all required acceptance thresholds |
| Proceed with conditions | Data is usable but documented corrections or controls are required |
| Stop | Critical schema, security, ownership, or quality problems prevent safe onboarding |

The thresholds used in this lab are practice thresholds. In real integrations they must be agreed with the data owner and consumer.

## Execution modes

### Local testing

Python and DuckDB process small synthetic files directly on the workstation.

### Docker testing

The same evaluator runs inside a container with the sample directory mounted read-only and output written to a mounted directory.

### AWS development adaptation

A later step can place synthetic files in S3 and query them using Athena and the Glue Data Catalog. This is optional and requires a reviewed cost-safe plan.

### Production architecture

A production version would use isolated partner landing prefixes, encryption, least-privilege IAM, schema versioning, durable quality results, monitoring, orchestration, and approved retention policies.

## Safety and cost

The initial implementation is entirely local and free.

Do not upload real customer or partner data. Do not create AWS resources during the local stage.

Athena and S3 are introduced only through a separate reviewed step because Athena charges by data scanned and S3 has storage and request costs.

## Definition of done

- Both sample datasets can be profiled repeatedly.
- Python tests pass.
- SQL checks return deterministic results.
- Invalid records contain machine-readable reasons.
- Counts reconcile from input to accepted and rejected output.
- The evaluation report contains evidence and a recommendation.
- Field mapping and data dictionary are complete.
- Local and Docker instructions are tested.
- No real personal data or secrets are committed.

## Tested commands

Run these commands from the repository root with the Python virtual environment active.

### Install the local SQL dependency

    python -m pip install 'duckdb>=1.1,<2'

DuckDB runs inside the local Python process. It does not require a server or cloud account.

### Run the automated tests

    make --directory partner-data-engineering-labs/01-partner-data-evaluation test

Expected result: 10 tests pass.

### Run the Python evaluation

    make --directory partner-data-engineering-labs/01-partner-data-evaluation local

This creates accepted records, rejected records, and `profile.json` under the ignored `output/` directory.

### Run the DuckDB SQL checks

    make --directory partner-data-engineering-labs/01-partner-data-evaluation sql

This additionally creates five CSV reports and `sql_summary.json`.

### Build the Docker image

    make --directory partner-data-engineering-labs/01-partner-data-evaluation docker-build

The image name is `partner-data-evaluation:local`.

### Run the Docker image

    make --directory partner-data-engineering-labs/01-partner-data-evaluation docker-run

The container runs with networking disabled and writes generated evidence to the mounted `output/` directory.

## Verified results

| Check | Result |
|---|---|
| Python tests | 10 passed |
| Customer reconciliation | 12 input = 4 accepted + 8 rejected |
| Event reconciliation | 13 input = 5 accepted + 8 rejected |
| Accepted-customer activity coverage | 100.00% |
| Event customer-reference match rate | 72.73% |
| Docker runtime network | Disabled |
| AWS services used | None |

## Generated local evidence

The following generated files are ignored by Git:

- `output/profile.json`
- `output/accepted_customers.jsonl`
- `output/rejected_customers.jsonl`
- `output/accepted_events.jsonl`
- `output/rejected_events.jsonl`
- `output/sql_summary.json`
- `output/sql/*.csv`

## Execution boundary

The completed checks prove that the evaluator works:

- Directly in local Python.
- Through local DuckDB SQL.
- Inside a reproducible Docker container.

They do not prove an AWS deployment or production deployment. No AWS service has been used in Lab 01.
