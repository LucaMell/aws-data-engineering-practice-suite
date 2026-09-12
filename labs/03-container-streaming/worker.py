import json
import os
import signal
import time

import boto3


running = True


def stop(*_):
    global running
    running = False


def aws_client(service_name):
    endpoint_url = os.getenv("AWS_ENDPOINT_URL")
    options = {"endpoint_url": endpoint_url} if endpoint_url else {}
    return boto3.client(service_name, **options)


def process_record(record, s3, sqs, sns):
    try:
        value = json.loads(record["Data"])
        email = value["email"].strip().lower()

        if "@" not in email:
            raise ValueError("invalid email")

        value["email"] = email
        s3.put_object(
            Bucket=os.environ["BUCKET"],
            Key=f"events/{value['event_id']}.json",
            Body=json.dumps(value),
        )
        return "stored"
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        sqs.send_message(
            QueueUrl=os.environ["QUEUE_URL"],
            MessageBody=str(exc),
        )
        sns.publish(
            TopicArn=os.environ["TOPIC_ARN"],
            Message=str(exc),
        )
        return "quarantined"


def main():
    kinesis = aws_client("kinesis")
    s3 = aws_client("s3")
    sqs = aws_client("sqs")
    sns = aws_client("sns")

    stream = os.environ["STREAM_NAME"]
    shards = kinesis.list_shards(StreamName=stream)["Shards"]
    if len(shards) != 1:
        raise RuntimeError("Practice ECS worker expects one shard")

    iterator = kinesis.get_shard_iterator(
        StreamName=stream,
        ShardId=shards[0]["ShardId"],
        ShardIteratorType="TRIM_HORIZON",
    )["ShardIterator"]

    while running:
        response = kinesis.get_records(
            ShardIterator=iterator,
            Limit=100,
        )
        iterator = response["NextShardIterator"]

        for record in response["Records"]:
            process_record(record, s3, sqs, sns)

        time.sleep(1)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, stop)
    main()
