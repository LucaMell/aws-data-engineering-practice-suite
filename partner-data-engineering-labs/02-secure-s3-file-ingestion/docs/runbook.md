# Secure File Ingestion Runbook

## Purpose

This runbook describes how to operate and troubleshoot the Lab 02 secure file
ingestion flow.

The current implementation uses synthetic files and local Moto-based S3
emulation.

No real AWS resources are required for the local workflow.

## Delivery components

Each complete practice delivery contains three objects:

    customers_YYYYMMDD_batchNNN.csv
    customers_YYYYMMDD_batchNNN.csv.sha256
    customers_YYYYMMDD_batchNNN.csv.complete

The CSV contains the data.

The `.sha256` file contains the expected SHA-256 checksum.

The `.complete` marker indicates that the upload has finished and the file is
ready to be evaluated.

## Storage stages

The ingestion flow uses these logical object prefixes:

    landing/
    validated/
    quarantined/
    archived/
    curated/

### landing/

New partner deliveries arrive here first.

### validated/

Files that passed required integrity and schema checks.

### quarantined/

Files that failed required checks.

### archived/

Original successful deliveries retained for audit and replay.

### curated/

Files approved for downstream consumption.

## Normal processing flow

For a new complete delivery:

1. The data file, checksum, and completion marker are uploaded to `landing/`.
2. The filename is checked.
3. The completion marker is checked.
4. The checksum file is checked.
5. The calculated checksum is compared with the expected checksum.
6. The CSV schema and field values are validated.
7. A successful file is copied to `validated/`.
8. The original successful delivery is copied to `archived/`.
9. The validated data is copied to `curated/`.

Expected status:

    validated

## Deferred delivery

A delivery is deferred when it does not yet have its completion marker.

Expected status:

    deferred

Expected reason:

    delivery_not_complete

Operational action:

- do not quarantine immediately;
- do not process the file;
- wait for the approved completion signal;
- investigate if the marker does not arrive within the expected delivery
  window.

## Duplicate delivery

A delivery is classified as a duplicate when the same delivery identity and
checksum have already been received.

Expected status:

    duplicate

Operational action:

- do not process the delivery again;
- do not create another logical ingestion;
- verify that the previous successful processing exists if investigation is
  required.

Duplicate detection provides idempotent behavior.

## Conflicting delivery

A conflict occurs when the same delivery filename is received with a different
checksum.

Expected status:

    conflict

Operational action:

1. Stop automatic processing for that delivery.
2. Preserve the conflicting evidence.
3. Compare the previous and new checksums.
4. Confirm which delivery is authoritative.
5. Do not silently overwrite the existing logical delivery.
6. Record the resolution.

## Quarantined delivery

A delivery may be quarantined for reasons including:

    invalid_filename
    checksum_file_missing
    invalid_checksum_file
    checksum_mismatch
    schema_validation_failed

Operational action:

1. Read the machine-readable reason.
2. Preserve the original delivery.
3. Review the validation errors.
4. Determine whether the sender must provide a corrected file.
5. Do not manually move the file into `validated/` without resolving the
   validation failure.

## Schema validation failures

Current validation checks include:

- expected CSV columns;
- required customer identifier;
- basic email format;
- allowed boolean consent values;
- parseable timestamps.

A schema failure includes detailed validation errors where available.

Example categories:

    required_value_missing
    invalid_email
    invalid_boolean
    invalid_timestamp
    invalid_columns

## Checksum mismatch

A checksum mismatch means that the calculated SHA-256 value differs from the
value supplied in the checksum file.

Operational action:

1. Do not process the file.
2. Confirm that the checksum belongs to the delivered file.
3. Confirm that neither file was changed after checksum creation.
4. Request a corrected delivery if necessary.

Do not regenerate the checksum simply to make an unexplained mismatch pass.

## Local validation commands

Run Lab 02 tests:

    make --directory partner-data-engineering-labs/02-secure-s3-file-ingestion test

Expected current result:

    27 passed

Run the complete repository test suite:

    python -m pytest -q

## Docker validation

Build the Lab 02 image:

    make --directory partner-data-engineering-labs/02-secure-s3-file-ingestion docker-build

Run the container:

    make --directory partner-data-engineering-labs/02-secure-s3-file-ingestion docker-run

The Docker container runs with networking disabled.

The Moto-based tests therefore cannot contact real AWS while running through
this Docker command.

## GitHub Actions validation

The repository `Validate suite`:

- runs Python tests;
- compiles Python files;
- validates Terraform syntax and formatting where applicable;
- builds Docker images;
- builds the Lab 01 and Lab 02 partner-data images.

The validation workflow does not deploy AWS resources.

Do not use the separate manual deployment workflow until its authentication,
cost, resource scope, and cleanup have been reviewed.

## Replay

The `archived/` prefix preserves successful original deliveries.

A controlled replay should:

1. identify the exact archived object;
2. record the replay reason;
3. verify its checksum;
4. confirm which processing version should be used;
5. run the approved processing path;
6. distinguish intentional replay from accidental duplicate delivery;
7. record the replay result.

The current practice implementation documents replay but does not yet provide a
dedicated replay command.

## Local cleanup

Moto test resources exist only inside mocked tests and disappear after each
test.

Docker containers are started with:

    --rm

so the container is removed after execution.

Local Docker images can be inspected with:

    docker images

Do not remove images or other local resources unless cleanup is intended.

## AWS development deployment

No real AWS development resource is part of the current Lab 02 implementation.

Before any AWS development deployment:

1. List every proposed AWS resource.
2. Review whether the resource is supported by the account plan.
3. Explain possible cost.
4. Prepare cleanup commands.
5. Receive explicit approval.
6. Deploy only synthetic practice data.
7. Validate the result.
8. Clean up immediately when the exercise is complete.
9. Verify that cleanup succeeded.

## Production operations

A production runbook would additionally define:

- expected delivery schedule;
- sender ownership and contacts;
- incident severity;
- retry policy;
- service-level expectations;
- alert thresholds;
- quarantine ownership;
- conflict-resolution procedure;
- retention periods;
- monitoring dashboards;
- audit-log locations;
- replay approval;
- escalation paths;
- disaster-recovery procedure.
