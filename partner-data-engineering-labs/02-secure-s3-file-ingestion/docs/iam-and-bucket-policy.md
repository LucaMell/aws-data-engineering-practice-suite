# IAM and Bucket Policy Design

## Purpose

This document shows example permissions for a secure partner-file ingestion
design.

These policies are design examples only.

They are not deployed by Lab 02.

## Principle of least privilege

Each identity should receive only the permissions required for its role.

The design separates:

- partner upload access;
- ingestion processing access;
- curated-data consumer access;
- bucket-level security enforcement.

Example names and account identifiers below are placeholders.

## Example resource layout

Assume a production bucket named:

    example-partner-ingestion-bucket

Objects are organized under:

    landing/
    validated/
    quarantined/
    archived/
    curated/

## Partner uploader

A partner uploader should normally be able to write only to its approved
landing prefix.

Example IAM policy:

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "WritePartnerLandingObjects",
          "Effect": "Allow",
          "Action": [
            "s3:PutObject"
          ],
          "Resource": [
            "arn:aws:s3:::example-partner-ingestion-bucket/landing/customers/*"
          ]
        }
      ]
    }

This example does not allow the partner to:

- read curated data;
- read archived data;
- read quarantine data;
- delete objects;
- modify bucket settings;
- modify IAM permissions.

Whether additional permissions are required depends on the selected upload
method.

## Ingestion processor

The ingestion process needs broader access because it reads incoming files and
routes them between processing stages.

Example IAM policy:

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "ReadLandingObjects",
          "Effect": "Allow",
          "Action": [
            "s3:GetObject"
          ],
          "Resource": [
            "arn:aws:s3:::example-partner-ingestion-bucket/landing/*"
          ]
        },
        {
          "Sid": "WritePipelineStages",
          "Effect": "Allow",
          "Action": [
            "s3:PutObject"
          ],
          "Resource": [
            "arn:aws:s3:::example-partner-ingestion-bucket/validated/*",
            "arn:aws:s3:::example-partner-ingestion-bucket/quarantined/*",
            "arn:aws:s3:::example-partner-ingestion-bucket/archived/*",
            "arn:aws:s3:::example-partner-ingestion-bucket/curated/*"
          ]
        }
      ]
    }

If the implementation uses S3 copy operations, the processor needs permission
to read the source object and write the destination object.

If successful landing objects are later deleted, `s3:DeleteObject` should be
added only for the exact approved landing prefix.

It is intentionally omitted from this example.

## Curated-data consumer

A downstream consumer may need only read access to curated data.

Example IAM policy:

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "ReadCuratedObjects",
          "Effect": "Allow",
          "Action": [
            "s3:GetObject"
          ],
          "Resource": [
            "arn:aws:s3:::example-partner-ingestion-bucket/curated/*"
          ]
        }
      ]
    }

The consumer does not need access to landing, quarantine, or archive objects.

## Secure transport enforcement

A bucket policy can reject requests that do not use TLS.

Example:

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "DenyInsecureTransport",
          "Effect": "Deny",
          "Principal": "*",
          "Action": "s3:*",
          "Resource": [
            "arn:aws:s3:::example-partner-ingestion-bucket",
            "arn:aws:s3:::example-partner-ingestion-bucket/*"
          ],
          "Condition": {
            "Bool": {
              "aws:SecureTransport": "false"
            }
          }
        }
      ]
    }

This policy does not grant access.

It only denies requests that use insecure transport.

IAM or another approved authorization mechanism must still grant the required
access.

## Public access

A production bucket used for partner ingestion should normally have S3 Block
Public Access enabled.

The pipeline does not require anonymous public access.

A public bucket or public object policy should not be used simply to make file
delivery easier.

## Encryption

S3 objects should be encrypted at rest.

A deployment must decide which encryption model is appropriate.

Possible approaches include:

- S3-managed encryption;
- KMS-managed encryption when additional key-level controls are required.

If KMS is used, both IAM permissions and the KMS key policy must permit the
required operation.

KMS configuration is intentionally not included in the local implementation.

## Prefix isolation

If multiple partners share a bucket, access can be divided further.

Example:

    landing/partner-a/
    landing/partner-b/

Each uploader should receive access only to its own assigned prefix.

Another option is separate buckets where stronger isolation is required.

The correct model depends on operational and security requirements.

## Listing permissions

`s3:ListBucket` is a bucket-level permission rather than an object-level
permission.

If an application requires object listing, access should be restricted with a
prefix condition where practical.

Example concept:

    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::example-partner-ingestion-bucket",
      "Condition": {
        "StringLike": {
          "s3:prefix": [
            "landing/customers/*"
          ]
        }
      }
    }

Do not grant unrestricted bucket listing unless it is required.

## Production review checklist

Before deploying real IAM or bucket policies, verify:

1. Which identity performs each operation.
2. Which exact S3 actions are required.
3. Which bucket and prefixes are required.
4. Whether object deletion is necessary.
5. Whether object listing is necessary.
6. Whether KMS permissions are required.
7. Whether TLS is enforced.
8. Whether S3 Block Public Access is enabled.
9. Whether cross-account access is involved.
10. Whether access logs or CloudTrail data events are required.
11. Whether policy changes have been reviewed.
12. Whether a cleanup and rollback procedure exists.

## Lab 02 boundary

The current Lab 02 implementation tests application behavior with Moto.

It does not prove:

- real IAM enforcement;
- real S3 bucket-policy enforcement;
- TLS enforcement;
- KMS permissions;
- cross-account access;
- production network controls.

Those require a separate reviewed AWS development or production environment.
