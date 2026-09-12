import importlib.util
import json
import os
from pathlib import Path


# Prevent accidental AWS credential discovery during tests.
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")


worker_path = Path(__file__).with_name("worker.py")
module_spec = importlib.util.spec_from_file_location(
    "lab3_worker",
    worker_path,
)

if module_spec is None or module_spec.loader is None:
    raise ImportError(f"Cannot load worker from {worker_path}")

worker = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(worker)


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


def configure_environment(monkeypatch):
    monkeypatch.setenv("BUCKET", "test-output-bucket")
    monkeypatch.setenv(
        "QUEUE_URL",
        "https://example.com/test-quarantine",
    )
    monkeypatch.setenv(
        "TOPIC_ARN",
        "arn:aws:sns:eu-west-1:123456789012:test-alerts",
    )


def make_record(payload):
    return {"Data": json.dumps(payload).encode("utf-8")}


def test_sample_event_id():
    sample_path = Path(__file__).parent / "sample/event.json"
    assert json.loads(sample_path.read_text())["event_id"] == "ecs-1"


def test_valid_record_is_written_to_s3(monkeypatch):
    configure_environment(monkeypatch)
    fake_s3 = FakeS3()
    fake_sqs = FakeSQS()
    fake_sns = FakeSNS()

    result = worker.process_record(
        make_record(
            {
                "event_id": "ecs-1",
                "customer_id": "customer-1",
                "email": " Luca@Example.com ",
                "amount": 25,
            }
        ),
        fake_s3,
        fake_sqs,
        fake_sns,
    )

    assert result == "stored"
    assert len(fake_s3.objects) == 1
    assert len(fake_sqs.messages) == 0
    assert len(fake_sns.messages) == 0

    stored_object = fake_s3.objects[0]
    assert stored_object["Bucket"] == "test-output-bucket"
    assert stored_object["Key"] == "events/ecs-1.json"

    stored_payload = json.loads(stored_object["Body"])
    assert stored_payload["email"] == "luca@example.com"


def test_invalid_record_is_sent_to_sqs_and_sns(monkeypatch):
    configure_environment(monkeypatch)
    fake_s3 = FakeS3()
    fake_sqs = FakeSQS()
    fake_sns = FakeSNS()

    result = worker.process_record(
        make_record(
            {
                "event_id": "ecs-2",
                "customer_id": "customer-2",
                "email": "invalid",
                "amount": 10,
            }
        ),
        fake_s3,
        fake_sqs,
        fake_sns,
    )

    assert result == "quarantined"
    assert len(fake_s3.objects) == 0
    assert len(fake_sqs.messages) == 1
    assert len(fake_sns.messages) == 1
    assert fake_sqs.messages[0]["MessageBody"] == "invalid email"
    assert fake_sns.messages[0]["Message"] == "invalid email"
