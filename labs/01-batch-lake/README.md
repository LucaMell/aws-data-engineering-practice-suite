# Lab 1: Batch lake

Native AWS uses S3, Glue Spark, Glue Catalog, and Athena. Docker runs the small equivalent transformation locally. Kubernetes runs that container as a CronJob; it is an alternative runtime, not a containerized Glue service.

1. `make test && make local`; inspect `output/orders.parquet`.
2. `docker build -t batch-lake .` to reproduce the runtime.
3. `cd terraform && terraform init && terraform apply`.
4. Upload `sample/orders.csv` to the output `data_bucket` under `bronze/orders.csv`.
5. Start the Glue job, inspect CloudWatch logs and the `silver/` prefix, then query it after creating an Athena table/crawler.
6. `terraform destroy`.

