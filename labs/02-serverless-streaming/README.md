# Lab 2: Serverless streaming

Kinesis triggers a ZIP Lambda; valid events go to S3, business-invalid events to SQS, and SNS receives an alert. Docker packages the identical handler as a Lambda image. Kubernetes requires a separate long-running Kinesis consumer, implemented properly in Lab 4.

Run Terraform, send each JSONL line with `aws kinesis put-record`, then inspect Lambda/CloudWatch, S3, SQS, and SNS metrics. Destroy afterwards. To practise container Lambda, push the Docker image to ECR and change `aws_lambda_function` to `package_type="Image"` plus `image_uri`.
