import json, os, boto3
from amazon_kclpy import kcl, v3

s3=boto3.client("s3"); sqs=boto3.client("sqs"); sns=boto3.client("sns")


class Processor(v3.RecordProcessorBase):
    def initialize(self, initialize_input):
        self.shard_id=initialize_input.shard_id
    def process_records(self, process_records_input):
        for record in process_records_input.records:
            try:
                value=json.loads(record.binary_data)
                if "@" not in value["email"]: raise ValueError("invalid email")
                s3.put_object(Bucket=os.environ["BUCKET"],Key=f"events/{value['event_id']}.json",Body=json.dumps(value))
            except (ValueError,KeyError,json.JSONDecodeError) as exc:
                sqs.send_message(QueueUrl=os.environ["QUEUE_URL"],MessageBody=str(exc))
                sns.publish(TopicArn=os.environ["TOPIC_ARN"],Message=str(exc))
        process_records_input.checkpointer.checkpoint()
    def lease_lost(self, lease_lost_input): pass
    def shard_ended(self, shard_ended_input): shard_ended_input.checkpointer.checkpoint()
    def shutdown_requested(self, shutdown_requested_input): shutdown_requested_input.checkpointer.checkpoint()


if __name__=="__main__":
    kcl.KCLProcess(Processor()).run()

