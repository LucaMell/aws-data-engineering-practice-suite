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


def process_data(data, s3, sqs, sns):
    try:
        value = json.loads(data)
        email = value["email"].strip().lower()

        if "@" not in email:
            raise ValueError("invalid email")

        value["email"] = email
        s3.put_object(
            Bucket=os.environ["BUCKET"],
            Key=f"events/{value['event_id']}.json",
            Body=json.dumps(value),
            ContentType="application/json",
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


def run_kinesis(s3, sqs, sns):
    kinesis = aws_client("kinesis")
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
            process_data(record["Data"], s3, sqs, sns)

        time.sleep(1)


def poll_sqs_once(input_queue_url, s3, sqs, sns):
    response = sqs.receive_message(
        QueueUrl=input_queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5,
        VisibilityTimeout=30,
    )

    messages = response.get("Messages", [])

    for message in messages:
        process_data(message["Body"], s3, sqs, sns)
        sqs.delete_message(
            QueueUrl=input_queue_url,
            ReceiptHandle=message["ReceiptHandle"],
        )

    return len(messages)


def run_sqs(s3, sqs, sns):
    input_queue_url = os.environ["INPUT_QUEUE_URL"]

    while running:
        poll_sqs_once(input_queue_url, s3, sqs, sns)


def main():
    s3 = aws_client("s3")
    sqs = aws_client("sqs")
    sns = aws_client("sns")

    input_mode = os.getenv("INPUT_MODE", "kinesis").lower()

    if input_mode == "kinesis":
        run_kinesis(s3, sqs, sns)
    elif input_mode == "sqs":
        run_sqs(s3, sqs, sns)
    else:
        raise ValueError(
            f"Unsupported INPUT_MODE: {input_mode}"
        )


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, stop)
    main()
