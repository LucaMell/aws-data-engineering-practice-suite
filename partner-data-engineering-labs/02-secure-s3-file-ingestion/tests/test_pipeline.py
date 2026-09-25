import os
import sys
from pathlib import Path

import boto3
from moto import mock_aws


os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")


LAB_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = LAB_DIR / "src"
SAMPLE_DIR = LAB_DIR / "sample"
SCHEMA_FILE = LAB_DIR / "schemas" / "customers.schema.json"

sys.path.insert(0, str(SRC_DIR))

from ingestion import load_schema
from pipeline import process_delivery


VALID_FILE = SAMPLE_DIR / "customers_20260925_batch001.csv"
INVALID_FILE = SAMPLE_DIR / "customers_20260925_batch002.csv"


def create_test_bucket():
    s3 = boto3.client("s3", region_name="eu-west-1")
    bucket = "partner-ingestion-test"

    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    return s3, bucket


@mock_aws
def test_valid_delivery_runs_through_full_pipeline():
    s3, bucket = create_test_bucket()
    schema = load_schema(SCHEMA_FILE)

    result = process_delivery(
        s3,
        bucket,
        VALID_FILE,
        schema,
    )

    assert result["status"] == "validated"

    response = s3.list_objects_v2(Bucket=bucket)

    keys = {
        item["Key"]
        for item in response.get("Contents", [])
    }

    assert (
        "landing/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
        in keys
    )

    assert (
        "validated/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
        in keys
    )

    assert (
        "archived/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
        in keys
    )

    assert (
        "curated/customers/2026/09/25/"
        "customers_20260925_batch001.csv"
        in keys
    )


@mock_aws
def test_invalid_delivery_runs_to_quarantine():
    s3, bucket = create_test_bucket()
    schema = load_schema(SCHEMA_FILE)

    result = process_delivery(
        s3,
        bucket,
        INVALID_FILE,
        schema,
    )

    assert result["status"] == "quarantined"
    assert (
        result["evaluation"]["reason"]
        == "schema_validation_failed"
    )

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="quarantined/",
    )

    assert response["KeyCount"] == 1


@mock_aws
def test_second_processing_of_same_delivery_is_duplicate():
    s3, bucket = create_test_bucket()
    schema = load_schema(SCHEMA_FILE)

    first = process_delivery(
        s3,
        bucket,
        VALID_FILE,
        schema,
    )

    second = process_delivery(
        s3,
        bucket,
        VALID_FILE,
        schema,
    )

    assert first["status"] == "validated"
    assert second == {
        "status": "duplicate",
        "evaluation": None,
    }
