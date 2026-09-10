import json, os, signal, time, boto3
running=True
def stop(*_):
    global running; running=False


def main():
    k=boto3.client("kinesis"); s3=boto3.client("s3"); sqs=boto3.client("sqs"); sns=boto3.client("sns")
    stream=os.environ["STREAM_NAME"]
    shards=k.list_shards(StreamName=stream)["Shards"]
    if len(shards)!=1: raise RuntimeError("Practice ECS worker expects one shard")
    it=k.get_shard_iterator(StreamName=stream,ShardId=shards[0]["ShardId"],ShardIteratorType="TRIM_HORIZON")["ShardIterator"]
    while running:
        response=k.get_records(ShardIterator=it,Limit=100); it=response["NextShardIterator"]
        for record in response["Records"]:
            try:
                value=json.loads(record["Data"]); email=value["email"].strip().lower()
                if "@" not in email: raise ValueError("invalid email")
                value["email"]=email
                s3.put_object(Bucket=os.environ["BUCKET"],Key=f"events/{value['event_id']}.json",Body=json.dumps(value))
            except (ValueError,KeyError,json.JSONDecodeError) as exc:
                sqs.send_message(QueueUrl=os.environ["QUEUE_URL"],MessageBody=str(exc))
                sns.publish(TopicArn=os.environ["TOPIC_ARN"],Message=str(exc))
        time.sleep(1)


if __name__=="__main__":
    signal.signal(signal.SIGTERM,stop); main()

