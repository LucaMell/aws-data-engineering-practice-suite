# Lab 02: Secure S3 File Ingestion

## Business scenario

An external data partner delivers files that must be ingested safely and
repeatably into S3-style object storage.

The ingestion process must determine whether each delivery is complete,
structurally valid, safe to accept, and already processed.

Valid files continue through the pipeline. Invalid or suspicious files are
quarantined with a clear reason.

Repeated delivery of the same file must not cause duplicate processing.

## Learning objectives

By completing this lab, you will practise:

- Designing secure partner file delivery into S3-style object storage.
- Understanding partner-push and internal-pull delivery patterns.
- Separating landing, validated, quarantined, archived, and curated objects.
- Designing predictable filename and object-key conventions.
- Calculating and verifying SHA-256 checksums.
- Detecting incomplete file deliveries.
- Implementing idempotent processing.
- Detecting duplicate deliveries.
- Validating file structure and schema.
- Quarantining invalid files with machine-readable reasons.
- Using Boto3 with S3-compatible object storage.
- Testing AWS-style behavior locally.
- Designing least-privilege IAM permissions.
- Understanding encryption in transit and at rest.
- Designing audit, retention, lifecycle, replay, and cleanup controls.
- Separating local testing, Docker testing, GitHub Actions, AWS development,
  and production deployment.

## Object-storage layout

The lab uses these logical prefixes:

    landing/
    validated/
    quarantined/
    archived/
    curated/

### landing/

Files that have arrived but have not yet passed ingestion checks.

### validated/

Files that passed file-level and schema-level validation.

### quarantined/

Files that failed validation or could not safely be processed.

### archived/

Original successfully processed deliveries retained for replay or audit.

### curated/

Normalized data that downstream consumers can use.

## Ingestion flow

    Partner delivery
           |
           v
       landing/
           |
           v
    Filename and object-key checks
           |
           v
    Checksum and completeness checks
           |
           v
    Duplicate / idempotency check
           |
           v
      Schema validation
          / \
         /   \
      valid   invalid
        |        |
        v        v
    validated/  quarantined/
        |
        v
    archived/
        |
        v
    curated/

## Delivery patterns

### Partner push

The external sender uploads a file into an approved landing location.

A production implementation could use mechanisms such as:

- tightly scoped S3 access;
- presigned upload URLs;
- managed file-transfer services.

The sender should never receive unnecessary access to other prefixes or
objects.

### Internal pull

An internal process retrieves a file from an approved external location and
places it in the landing prefix.

The same validation and idempotency controls should run after the file enters
the landing area.

The local implementation will model both patterns without contacting an
external system.

## Filename convention

Practice files will follow a predictable convention:

    customers_YYYYMMDD_batchNNN.csv

Example:

    customers_20260925_batch001.csv

The filename helps operations and troubleshooting, but the ingestion process
must not rely on the filename alone to determine correctness.

## Object-key convention

Objects use prefixes and delivery dates so their purpose is clear.

Examples:

    landing/customers/2026/09/25/customers_20260925_batch001.csv
    validated/customers/2026/09/25/customers_20260925_batch001.csv
    archived/customers/2026/09/25/customers_20260925_batch001.csv

Quarantined objects retain information linking them to the original delivery.

## Checksums

The lab calculates a SHA-256 checksum for each delivered file.

The checksum provides a deterministic fingerprint that can help with:

- detecting duplicate deliveries;
- checking file integrity;
- recording processing history;
- supporting replay and audit investigations.

A checksum does not replace encryption or access control.

## File-completeness checks

A file should not be processed while it may still be uploading.

The local lab will model a completeness signal separately from the data file.

A production implementation could use:

- a manifest file;
- a completion marker;
- an atomic upload workflow;
- an event generated only after a completed object upload.

## Idempotency

Running ingestion more than once for the same delivery must not create
duplicate results.

The lab will use deterministic file identity information such as:

- object key;
- checksum;
- delivery metadata.

Repeated deliveries will be classified explicitly instead of silently
processed again.

## Schema validation

Files will be checked against a defined schema.

Validation will include checks such as:

- required columns;
- expected column names;
- required identifiers;
- expected data formats;
- malformed rows.

Files that fail required checks will be quarantined.

## Execution modes

### Local testing

Python and a local AWS emulator are used first.

No real AWS credentials or AWS resources are required.

### Docker testing

The same ingestion logic runs in a reproducible non-root container.

Docker testing remains local and does not require real AWS credentials.

### GitHub Actions

GitHub Actions runs automated validation and builds the Lab 02 Docker image.

The validation workflow does not deploy AWS resources.

### AWS development adaptation

A later optional step can test the design with a small S3 development setup.

Before creating any AWS resource:

1. Proposed resources must be reviewed.
2. Expected cost and Free-plan implications must be explained.
3. Explicit approval is required.
4. Cleanup commands must be prepared in advance.

No AWS resource is created during the initial Lab 02 implementation.

### Production architecture

A production implementation would additionally consider:

- dedicated partner access boundaries;
- least-privilege IAM roles and policies;
- S3 Block Public Access;
- encryption at rest;
- TLS for transport;
- centrally managed encryption keys where required;
- object versioning where appropriate;
- CloudTrail or equivalent audit logging;
- lifecycle and retention rules;
- monitoring and alerting;
- controlled replay procedures;
- infrastructure as code;
- environment separation.

## Security principles

The design follows these principles:

- no public bucket access;
- no embedded AWS credentials;
- least privilege;
- encrypted transport;
- encrypted storage;
- synthetic practice data only;
- deterministic validation;
- explicit quarantine;
- traceable processing decisions;
- controlled retention and cleanup.

## Planned lab contents

The completed lab will contain:

    README.md
    src/
    tests/
    sample/
    schemas/
    docs/
    Dockerfile
    Makefile
    requirements.txt

Generated runtime output will remain outside version control.

## Definition of done

Lab 02 is complete when:

- synthetic partner files can be delivered into simulated object storage;
- landing, validated, quarantined, archived, and curated prefixes are used;
- filenames and object keys are validated;
- SHA-256 checksums are calculated and verified;
- incomplete deliveries are rejected or deferred safely;
- duplicate delivery does not create duplicate processing;
- valid files pass schema validation;
- invalid files are quarantined with a reason;
- automated tests pass locally;
- Docker execution is verified;
- GitHub Actions validates the lab without deploying AWS resources;
- least-privilege IAM and bucket-policy examples are documented;
- encryption, audit, retention, lifecycle, replay, and cleanup are documented;
- AWS development deployment remains a separate reviewed step;
- production differences are clearly documented.

## Safety and cost

The initial Lab 02 implementation is entirely local.

Do not create S3 buckets, IAM resources, KMS keys, CloudTrail trails, transfer
services, or other AWS resources during the local stage.

A real AWS development test will be considered separately only after its
security, cleanup procedure, and cost have been reviewed.

## Tested commands

Run the Lab 02 tests locally:

    make --directory partner-data-engineering-labs/02-secure-s3-file-ingestion test

Build the Docker image:

    make --directory partner-data-engineering-labs/02-secure-s3-file-ingestion docker-build

Run the tests inside Docker:

    make --directory partner-data-engineering-labs/02-secure-s3-file-ingestion docker-run

The Docker container runs with networking disabled.

## Verified results

| Check | Result |
|---|---|
| Local Lab 02 tests | 27 passed |
| Docker Lab 02 tests | 27 passed |
| Simulated object storage | Moto |
| Docker runtime network | Disabled |
| Duplicate-delivery handling | Verified |
| Conflicting-delivery detection | Verified |
| Incomplete-delivery handling | Verified |
| Schema quarantine | Verified |
| `landing/` prefix | Verified |
| `validated/` prefix | Verified |
| `quarantined/` prefix | Verified |
| `archived/` prefix | Verified |
| `curated/` prefix | Verified |
| Real AWS services used | None |

## Current execution boundary

The completed implementation currently proves the ingestion behavior:

- directly in local Python;
- with Boto3 against Moto-emulated S3;
- inside a reproducible non-root Docker container;
- with Docker networking disabled.

It does not prove a real AWS deployment or a production deployment.

A real AWS development test remains a separate optional step requiring a
cost, security, resource, and cleanup review before anything is created.
