# Lab 4: Kubernetes streaming with KCL

KCL coordinates Kinesis shard leases and checkpoints through DynamoDB, allowing multiple pods. Terraform creates the data services; an existing EKS cluster, ECR repository, and workload-identity role are prerequisites. Build/push the image, replace manifest placeholders, update `kcl.properties` stream name, and `kubectl apply -f kubernetes.yaml`.

The Docker image is also locally buildable. Native/serverless alternative: Lab 2. Before production, add explicit IAM permissions for Kinesis, DynamoDB KCL lease tables, CloudWatch, S3, SQS, and SNS to the pod role.
