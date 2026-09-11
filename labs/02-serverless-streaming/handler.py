import base64
import json
import os

import boto3


endpoint_url = os.getenv("AWS_ENDPOINT_URL")
client_options = {"endpoint_url": endpoint_url} if endpoint_url else {}

s3 = boto3.client("s3", **client_options)
sqs = boto3.client("sqs", **client_options)
sns = boto3.client("sns", **client_options)


def extract_payload(record):
    """Read either a Kinesis record or an SQS record."""

    if "kinesis" in record:
        encoded_data = record["kinesis"]["data"]
        decoded_data = base64.b64decode(encoded_data)
        return json.loads(decoded_data)

    if "body" in record:
        return json.loads(record["body"])

    raise ValueError("unsupported event source")


def lambda_handler(event, context):
    failures = []

    for record in event["Records"]:
        try:
            payload = extract_payload(record)

            email = payload["email"].strip().lower()

            if "@" not in email:
                raise ValueError("invalid email")

            payload["email"] = email

            s3.put_object(
                Bucket=os.environ["BUCKET"],
                Key=f"events/{payload['event_id']}.json",
                Body=json.dumps(payload),
                ContentType="application/json",
            )

        except (ValueError, KeyError, json.JSONDecodeError) as error:
            sqs.send_message(
                QueueUrl=os.environ["QUEUE_URL"],
                MessageBody=json.dumps(
                    {
                        "error": str(error),
                        "record": record,
                    }
                ),
            )

            sns.publish(
                TopicArn=os.environ["TOPIC_ARN"],
                Message=str(error),
            )

        except Exception:
            record_id = record.get("messageId") or record.get("eventID")

            if record_id:
                failures.append({"itemIdentifier": record_id})
            else:
                raise

    return {"batchItemFailures": failures}
