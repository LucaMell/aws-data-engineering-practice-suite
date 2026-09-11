import base64
import json
import os

# Prevent boto3 from looking for real AWS credentials during unit tests.
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

import importlib.util
from pathlib import Path


handler_path = Path(__file__).with_name("handler.py")

module_spec = importlib.util.spec_from_file_location(
    "lab2_handler",
    handler_path,
)

if module_spec is None or module_spec.loader is None:
    raise ImportError(f"Cannot load handler from {handler_path}")

handler = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(handler)

class FakeS3:
    def __init__(self):
        self.objects = []

    def put_object(self, **kwargs):
        self.objects.append(kwargs)


class FakeSQS:
    def __init__(self):
        self.messages = []

    def send_message(self, **kwargs):
        self.messages.append(kwargs)


class FakeSNS:
    def __init__(self):
        self.messages = []

    def publish(self, **kwargs):
        self.messages.append(kwargs)


def make_kinesis_event(payload, event_id):
    encoded_payload = base64.b64encode(
        json.dumps(payload).encode("utf-8")
    ).decode("utf-8")

    return {
        "Records": [
            {
                "eventID": event_id,
                "kinesis": {
                    "data": encoded_payload
                },
            }
        ]
    }


def configure_test_environment(monkeypatch):
    fake_s3 = FakeS3()
    fake_sqs = FakeSQS()
    fake_sns = FakeSNS()

    monkeypatch.setattr(handler, "s3", fake_s3)
    monkeypatch.setattr(handler, "sqs", fake_sqs)
    monkeypatch.setattr(handler, "sns", fake_sns)

    monkeypatch.setenv("BUCKET", "test-output-bucket")
    monkeypatch.setenv("QUEUE_URL", "https://example.com/test-queue")
    monkeypatch.setenv("TOPIC_ARN", "arn:aws:sns:eu-west-1:123456789012:test")

    return fake_s3, fake_sqs, fake_sns


def test_valid_event_is_written_to_s3(monkeypatch):
    fake_s3, fake_sqs, fake_sns = configure_test_environment(monkeypatch)

    event = make_kinesis_event(
        {
            "event_id": "e-1",
            "customer_id": "c-1",
            "email": " Luca@Example.com ",
            "amount": 25,
        },
        event_id="kinesis-record-1",
    )

    response = handler.lambda_handler(event, None)

    assert response == {"batchItemFailures": []}

    assert len(fake_s3.objects) == 1
    assert len(fake_sqs.messages) == 0
    assert len(fake_sns.messages) == 0

    stored_object = fake_s3.objects[0]

    assert stored_object["Bucket"] == "test-output-bucket"
    assert stored_object["Key"] == "events/e-1.json"

    stored_payload = json.loads(stored_object["Body"])

    assert stored_payload["email"] == "luca@example.com"


def test_invalid_event_is_sent_to_sqs_and_sns(monkeypatch):
    fake_s3, fake_sqs, fake_sns = configure_test_environment(monkeypatch)

    event = make_kinesis_event(
        {
            "event_id": "e-2",
            "customer_id": "c-2",
            "email": "invalid",
            "amount": 10,
        },
        event_id="kinesis-record-2",
    )

    response = handler.lambda_handler(event, None)

    assert response == {"batchItemFailures": []}

    assert len(fake_s3.objects) == 0
    assert len(fake_sqs.messages) == 1
    assert len(fake_sns.messages) == 1

    quarantine_message = json.loads(
        fake_sqs.messages[0]["MessageBody"]
    )

    assert quarantine_message["error"] == "invalid email"
    assert fake_sns.messages[0]["Message"] == "invalid email"