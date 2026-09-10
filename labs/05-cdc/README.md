# Lab 5: Change data capture

Native AWS: an existing logical-replication-enabled RDS PostgreSQL endpoint → DMS full-load-and-CDC task → Parquet in S3. Supply the existing DMS source endpoint, subnet group, and security groups to Terraform. Start the task manually after verifying endpoints.

Docker: PostgreSQL + Kafka + Debezium Connect. `make local`, update a customer with `psql`, and consume `practice.public.customers` from Kafka. Kubernetes: the manifest requires the Strimzi operator and an image containing the Debezium PostgreSQL connector. Secrets syntax is illustrative and must match the installed Strimzi secret provider.

DMS is not Dockerized; Debezium is the local/Kubernetes equivalent. Destroy DMS immediately after practice because the replication instance is billed while running.

