# Change summary

Describe what changed and why.

## Change type

- [ ] Python, SQL, or transformation
- [ ] Tests or sample data
- [ ] Documentation or data contract
- [ ] Docker packaging
- [ ] Terraform or AWS architecture
- [ ] CI/CD workflow
- [ ] Bug fix

## Execution mode tested

Select only modes that were actually tested.

- [ ] Static validation
- [ ] Local Python or SQL
- [ ] Local Docker
- [ ] Local AWS emulator
- [ ] Development AWS
- [ ] Production

## Verification

Command:

Result:

- [ ] Unit tests pass.
- [ ] Invalid-data behavior was tested.
- [ ] Counts reconcile.
- [ ] Retry, replay, and duplicate behavior were considered.
- [ ] Emulated services are not described as real AWS tests.

## Data, documentation, and security

- [ ] Schema and field mappings are updated.
- [ ] The data dictionary and runbook are updated.
- [ ] Quality rules are tested.
- [ ] Sample data contains no real sensitive data.
- [ ] No credentials, tokens, or private keys are committed.
- [ ] Logs do not expose sensitive payloads.
- [ ] IAM follows least privilege.

## Infrastructure and cost

- [ ] Terraform is formatted and validated.
- [ ] The Terraform plan was inspected.
- [ ] Cost and Free-plan compatibility are documented.
- [ ] Paid resources require explicit approval before apply.
- [ ] Cleanup instructions exist.
- [ ] Generated state, plans, and `.terraform/` are ignored.
- [ ] `.terraform.lock.hcl` is committed where applicable.

## Deployment safety

- [ ] Validation CI does not deploy.
- [ ] AWS deployment uses short-lived identity such as OIDC.
- [ ] Development and production are separated.
- [ ] Production requires approval.
- [ ] Rollback or forward-fix steps exist.

## Evidence, risks, and follow-up

Add non-sensitive test evidence and list remaining limitations or risks.
