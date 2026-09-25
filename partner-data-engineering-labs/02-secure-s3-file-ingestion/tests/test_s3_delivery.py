import importlib.util
import os
from pathlib import Path

import boto3
from moto import mock_aws


os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")


LAB_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = LAB_DIR / "src" / "s3_delivery.py"
SAMPLE_FILE = (
    LAB_DIR
    / "sample"
    / "customers_20260925_batch001.csv"
)


spec = importlib.util.spec_from_file_location(
    "lab02_s3_delivery",
    MODULE_PATH,
)

if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load S3 module from {MODULE_PATH}")

s3_delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s3_delivery)


def test_build_landing_key():
    key = s3_delivery.build_landing_key(SAMPLE_FILE.name)

    assert key == (
        "landing/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )


@mock_aws
def test_delivery_is_uploaded_to_simulated_s3():
    s3 = boto3.client("s3", region_name="eu-west-1")

    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    uploaded_keys = s3_delivery.upload_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="landing/",
    )

    stored_keys = sorted(
        item["Key"]
        for item in response.get("Contents", [])
    )

    assert sorted(uploaded_keys) == stored_keys

    assert stored_keys == [
        (
            "landing/customers/2026/09/25/"
            "customers_20260925_batch001.csv"
        ),
        (
            "landing/customers/2026/09/25/"
            "customers_20260925_batch001.csv.complete"
        ),
        (
            "landing/customers/2026/09/25/"
            "customers_20260925_batch001.csv.sha256"
        ),
    ]


@mock_aws
def test_same_delivery_is_detected_as_duplicate():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    assert (
        s3_delivery.classify_delivery(
            s3,
            bucket,
            SAMPLE_FILE,
        )
        == "new"
    )

    s3_delivery.upload_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    assert (
        s3_delivery.classify_delivery(
            s3,
            bucket,
            SAMPLE_FILE,
        )
        == "duplicate"
    )


@mock_aws
def test_same_filename_with_different_checksum_is_conflict(tmp_path):
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    s3_delivery.upload_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    changed_file = tmp_path / SAMPLE_FILE.name
    changed_file.write_text(
        "customer_id,email,country,consent,updated_at\n"
        "CUST999,changed@example.com,DK,true,2026-09-25T12:00:00Z\n",
        encoding="utf-8",
    )

    changed_checksum = (
        tmp_path / f"{SAMPLE_FILE.name}.sha256"
    )
    changed_checksum.write_text(
        f"{'0' * 64}  {SAMPLE_FILE.name}\n",
        encoding="utf-8",
    )

    assert (
        s3_delivery.classify_delivery(
            s3,
            bucket,
            changed_file,
        )
        == "conflict"
    )


@mock_aws
def test_ingest_delivery_uploads_new_file_only_once():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    first_result = s3_delivery.ingest_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    second_result = s3_delivery.ingest_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    assert first_result["status"] == "uploaded"
    assert len(first_result["uploaded_keys"]) == 3

    assert second_result == {
        "status": "duplicate",
        "uploaded_keys": [],
    }

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="landing/",
    )

    assert response["KeyCount"] == 3


def test_build_stage_keys():
    filename = "customers_20260925_batch001.csv"

    assert s3_delivery.build_stage_key(
        "landing",
        filename,
    ) == (
        "landing/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )

    assert s3_delivery.build_stage_key(
        "validated",
        filename,
    ) == (
        "validated/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )

    assert s3_delivery.build_stage_key(
        "quarantined",
        filename,
    ) == (
        "quarantined/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )

    assert s3_delivery.build_stage_key(
        "archived",
        filename,
    ) == (
        "archived/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )

    assert s3_delivery.build_stage_key(
        "curated",
        filename,
    ) == (
        "curated/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )


def test_build_stage_key_rejects_unknown_stage():
    try:
        s3_delivery.build_stage_key(
            "random-place",
            "customers_20260925_batch001.csv",
        )
    except ValueError as error:
        assert str(error) == "unsupported stage: random-place"
    else:
        raise AssertionError("Expected ValueError")


@mock_aws
def test_landing_file_can_be_copied_to_validated():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    s3_delivery.upload_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    validated_key = s3_delivery.copy_delivery_to_stage(
        s3,
        bucket,
        SAMPLE_FILE.name,
        "validated",
    )

    response = s3.list_objects_v2(
        Bucket=bucket,
    )

    stored_keys = {
        item["Key"]
        for item in response.get("Contents", [])
    }

    assert (
        "landing/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
        in stored_keys
    )

    assert (
        "validated/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
        in stored_keys
    )

    assert validated_key == (
        "validated/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )


@mock_aws
def test_invalid_delivery_can_be_copied_to_quarantine():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    invalid_file = (
        LAB_DIR
        / "sample"
        / "customers_20260925_batch002.csv"
    )

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    s3_delivery.upload_delivery(
        s3,
        bucket,
        invalid_file,
    )

    quarantined_key = s3_delivery.copy_delivery_to_stage(
        s3,
        bucket,
        invalid_file.name,
        "quarantined",
    )

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="quarantined/",
    )

    stored_keys = [
        item["Key"]
        for item in response.get("Contents", [])
    ]

    assert quarantined_key in stored_keys

    assert quarantined_key == (
        "quarantined/customers/2026/09/25/"
        "customers_20260925_batch002.csv"
    )


@mock_aws
def test_validated_decision_routes_to_validated_prefix():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    s3_delivery.upload_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    result = s3_delivery.route_delivery(
        s3,
        bucket,
        SAMPLE_FILE.name,
        {
            "status": "validated",
            "reason": "all_checks_passed",
        },
    )

    assert result == {
        "status": "validated",
        "destination_key": (
            "validated/customers/2026/09/25/"
            "customers_20260925_batch001.csv"
        ),
    }


@mock_aws
def test_deferred_decision_stays_in_landing():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    s3_delivery.upload_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    result = s3_delivery.route_delivery(
        s3,
        bucket,
        SAMPLE_FILE.name,
        {
            "status": "deferred",
            "reason": "delivery_not_complete",
        },
    )

    assert result == {
        "status": "deferred",
        "destination_key": None,
    }

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="validated/",
    )

    assert response["KeyCount"] == 0


@mock_aws
def test_valid_delivery_can_be_archived():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    s3_delivery.upload_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    archived_key = s3_delivery.archive_delivery(
        s3,
        bucket,
        SAMPLE_FILE.name,
    )

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="archived/",
    )

    stored_keys = [
        item["Key"]
        for item in response.get("Contents", [])
    ]

    assert archived_key == (
        "archived/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )

    assert archived_key in stored_keys


@mock_aws
def test_validated_file_can_be_copied_to_curated():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    s3_delivery.upload_delivery(
        s3,
        bucket,
        SAMPLE_FILE,
    )

    s3_delivery.copy_delivery_to_stage(
        s3,
        bucket,
        SAMPLE_FILE.name,
        "validated",
    )

    curated_key = s3_delivery.copy_between_stages(
        s3,
        bucket,
        SAMPLE_FILE.name,
        "validated",
        "curated",
    )

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="curated/",
    )

    stored_keys = [
        item["Key"]
        for item in response.get("Contents", [])
    ]

    assert curated_key == (
        "curated/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
    )

    assert curated_key in stored_keys
