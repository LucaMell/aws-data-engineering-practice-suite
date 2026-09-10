# Lab 6: S3 and Redshift warehouse

Terraform creates a landing bucket and private Redshift Serverless workgroup. Upload CSV, create `raw.orders`, use `COPY` with an IAM role, then run dbt to build and test `analytics.customer_revenue`.

Docker packages dbt. Kubernetes runs the same image as a CronJob. Native alternatives are Glue jobs or Redshift scheduled queries. Store credentials in Secrets Manager/GitHub secrets, never Git. The generated practice password is a sensitive Terraform output; production should use Secrets Manager rotation. Destroy the workgroup after practice.
