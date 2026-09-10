# AWS setup and operating guide

## 1. Prepare a sandbox

Use a non-production AWS account. In Billing, create a small monthly budget with email alerts. Configure IAM Identity Center/SSO and verify the selected identity:

```bash
aws configure sso --profile data-lab-dev
aws sso login --profile data-lab-dev
AWS_PROFILE=data-lab-dev aws sts get-caller-identity
```

Never place access keys, database passwords, account IDs, or personal data in Git.

## 2. Install local tools

Install Git, Python 3.11+, Docker, Terraform 1.7+, AWS CLI v2, and optionally `kubectl`, `eksctl`, Maven, `psql`, and dbt. From the suite root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest -q
```

## 3. Terraform state

For solo disposable practice, local state is acceptable. For GitHub Actions or a team, create an encrypted/versioned S3 state bucket and locking mechanism, then add a backend block to each Terraform root. State can contain sensitive values; restrict it tightly.

## 4. Native AWS deployment

Enter only one lab's `terraform` directory. Supply required variables in an uncommitted `terraform.auto.tfvars`, run `terraform fmt`, `init`, `validate`, and `plan`, inspect every proposed resource, then apply. Do not apply all seven labs together.

```bash
terraform fmt
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

Use CloudWatch Logs and service metrics to observe runs. Verify output data and failure paths, not only the green job status.

## 5. Container deployment

Create one ECR repository per deployable image, authenticate Docker, build, tag with the Git commit, scan, and push:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR="$ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com"
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin "$ECR"
docker build -t "$ECR/NAME:GIT_SHA" .
docker push "$ECR/NAME:GIT_SHA"
```

Production should promote an immutable digest that was already tested in dev.

## 6. Kubernetes/EKS deployment

The suite assumes an existing EKS cluster. Creating a secure cluster requires choices about VPC design, private endpoints, node groups versus Fargate, add-ons, logging, upgrades, and cost. Configure EKS Pod Identity or IRSA so pods receive AWS permissions without static keys. Replace manifest placeholders, review them, then apply:

```bash
aws eks update-kubeconfig --name YOUR_CLUSTER --region eu-west-1
kubectl diff -f kubernetes.yaml
kubectl apply -f kubernetes.yaml
kubectl rollout status deployment/NAME
kubectl logs deployment/NAME --follow
```

Glue, Lambda, DMS, Redshift, Kinesis, SQS, SNS, S3, and OpenSearch are not installed into EKS. Kubernetes hosts only the custom processor or orchestration component.

## 7. GitHub Actions

Create `dev` and `production` GitHub Environments. Configure an AWS OIDC provider and separate deploy roles with trust restricted to the repository and environment. Store the deploy-role ARN as `AWS_DEPLOY_ROLE_ARN`. For labs with required Terraform variables, store valid HCL assignments as the protected `TERRAFORM_TFVARS` environment secret.

Protect production with required reviewers. A pull request runs tests and validation; a manual deployment selects one lab and one environment.

## 8. Verification checklist

- Valid records arrive in the expected destination.
- Invalid records reach quarantine/DLQ.
- Retriable failures are retried and visible.
- Record counts reconcile from source to destination.
- Duplicate replay is understood and safe.
- IAM denies unrelated resources.
- Logs contain identifiers but no secrets/PII payloads.
- Metrics and alarms expose lag, errors, throttling, and cost.

## 9. Cleanup

Stop applications first, empty lab buckets if Terraform cannot remove them, then destroy from the same state:

```bash
terraform plan -destroy
terraform destroy
```

Confirm that EKS workloads, DMS instances, Redshift workgroups, OpenSearch domains, Flink applications, NAT gateways, load balancers, ECR images, log groups, and unattached storage are gone.

