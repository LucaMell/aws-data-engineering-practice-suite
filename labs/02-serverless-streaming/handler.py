import base64, json, os, boto3
s3, sqs, sns = boto3.client("s3"), boto3.client("sqs"), boto3.client("sns")


def lambda_handler(event, context):
    failures = []
    for record in event["Records"]:
        try:
            payload = json.loads(base64.b64decode(record["kinesis"]["data"]))
            email = payload["email"].strip().lower()
            if "@" not in email:
                raise ValueError("invalid email")
            payload["email"] = email
            s3.put_object(Bucket=os.environ["BUCKET"], Key=f"events/{payload['event_id']}.json", Body=json.dumps(payload))
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            sqs.send_message(QueueUrl=os.environ["QUEUE_URL"], MessageBody=json.dumps({"error":str(exc),"record":record}))
            sns.publish(TopicArn=os.environ["TOPIC_ARN"], Message=str(exc))
        except Exception:
            failures.append({"itemIdentifier": record["eventID"]})
    return {"batchItemFailures": failures}

