# Security and Production Design

## Purpose

This document describes how the local Lab 02 design maps to a secure AWS
development environment and to a production implementation.

The current lab uses Moto and synthetic data only. No real AWS resources are
required for the local implementation.

## Access model

Access should follow least privilege.

A partner that pushes files should receive access only to the location needed
for delivery.

For example, a partner uploader might be allowed to write only to:

    landing/customers/*

It should not normally be able to:

- list unrelated objects;
- read curated data;
- read archived files;
- read quarantined files;
- delete historical deliveries;
- change bucket configuration;
- change IAM policies.

Internal processing roles should receive only the permissions needed for their
pipeline stage.

## Example permission separation

### Partner upload identity

Typical permissions:

- write new landing objects;
- optionally read object metadata required by the upload mechanism.

It should not receive broad bucket administration permissions.

### Ingestion processor

Typical permissions:

- read landing objects;
- read checksum and completion-marker objects;
- write validated objects;
- write quarantined objects;
- write archive objects;
- delete landing objects only if the approved workflow requires cleanup.

### Downstream consumer

Typical permissions:

- read curated objects only.

This separation limits the effect of accidental or unauthorized actions.

## Bucket policy principles

A production bucket policy should normally:

- block requests that do not use secure transport;
- avoid anonymous or public access;
- permit only approved principals;
- avoid wildcard administrative permissions;
- restrict partner identities to their assigned prefixes.

S3 Block Public Access should remain enabled unless a reviewed requirement
explicitly requires otherwise.

## Secure transport

Production S3 access should use HTTPS/TLS.

A bucket policy can explicitly deny requests when:

    aws:SecureTransport = false

The local Moto environment does not prove TLS enforcement. It only tests the
application behavior.

## Encryption at rest

S3 encrypts stored objects at rest.

A production design should explicitly decide whether to use:

- S3-managed encryption;
- KMS-managed encryption where key-level control is required.

KMS introduces additional permissions, operational responsibilities, and
potential cost, so it is not introduced into this local lab.

## Credentials

Credentials must never be embedded in source code, Docker images, sample
files, Terraform files, or Git history.

Local Moto tests use dummy values such as:

    AWS_ACCESS_KEY_ID=testing
    AWS_SECRET_ACCESS_KEY=testing

These values are not real credentials.

AWS development workloads should use the configured authentication mechanism
for the environment.

Automated GitHub deployment should prefer short-lived identity mechanisms such
as OIDC rather than stored long-lived AWS access keys.

## File integrity

Each practice delivery contains:

- the data file;
- a SHA-256 checksum sidecar;
- a completion marker.

The checksum detects accidental content changes and supports duplicate
detection.

A checksum alone does not prove who created a file. Production integrations
with stronger authenticity requirements may additionally use signed manifests
or another approved authenticity mechanism.

## Completeness

The pipeline does not process a delivery until the completion signal exists.

This protects against processing a file while an uploader may still be
writing it.

Production alternatives include:

- completion-marker objects;
- delivery manifests;
- atomic transfer processes;
- completed-object events.

## Idempotency

A delivery is classified using its filename and checksum.

The current lab distinguishes:

- new delivery;
- duplicate delivery;
- conflicting delivery.

A duplicate does not create another logical ingestion.

A conflict means that the same delivery identity is associated with different
content and requires investigation.

## Quarantine

Invalid deliveries are separated from valid data.

Quarantine reasons should be machine-readable and auditable.

Examples include:

- invalid filename;
- missing checksum;
- checksum mismatch;
- invalid checksum format;
- schema validation failure.

Production systems should restrict access to quarantined data because it may
contain malformed or sensitive information.

## Auditability

A production implementation should retain enough information to answer:

- who delivered the file;
- when it arrived;
- which object key was used;
- which checksum was received;
- which checksum was calculated;
- which validation rules ran;
- whether it was validated, quarantined, deferred, duplicate, or conflicting;
- when it was archived;
- whether it was replayed.

Possible AWS audit sources include CloudTrail and application logs.

S3 data-event logging can add cost and should be reviewed before enabling it
for a development lab.

## Retention and lifecycle

Different prefixes can have different retention requirements.

Example policy concepts:

    landing/       short retention after successful processing
    validated/     retained while needed for processing
    quarantined/   retained long enough for investigation
    archived/      retained according to replay and audit requirements
    curated/       retained according to downstream data requirements

Production retention values must come from approved business, security, legal,
and compliance requirements.

Lifecycle rules should not be added blindly because deletion or archival can
affect replay and audit requirements.

## Replay

The archive prefix preserves the original successful delivery.

A replay procedure should:

1. identify the archived delivery;
2. record why replay is required;
3. verify the archived checksum;
4. run the current approved processing logic;
5. prevent the replay from being mistaken for an accidental duplicate;
6. record the replay result.

The current lab documents this behavior but does not yet implement a dedicated
replay command.

## Cleanup

Local Moto resources disappear automatically when each mocked test completes.

Docker test containers use:

    --rm

so the test container is removed after execution.

A real AWS development test must have explicit cleanup commands prepared before
resources are created.

Cleanup should verify that temporary resources were actually removed.

## AWS development option

A future cost-reviewed development exercise could use:

- one small S3 bucket;
- synthetic files only;
- S3 Block Public Access;
- default encryption;
- narrowly scoped IAM permissions;
- a small number of object requests;
- immediate cleanup after validation.

No AWS development deployment is part of the current local Lab 02 work.

## Production differences

The local lab proves application behavior, but it does not prove production
security.

A production implementation would normally add:

- environment-specific infrastructure as code;
- isolated identities and roles;
- reviewed bucket policies;
- encryption policy enforcement;
- centralized logging;
- monitoring and alerting;
- approved retention rules;
- durable processing-state storage;
- operational dashboards;
- controlled replay;
- incident procedures;
- tested disaster-recovery procedures.
