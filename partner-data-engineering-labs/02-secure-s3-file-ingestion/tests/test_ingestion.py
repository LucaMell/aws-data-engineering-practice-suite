import importlib.util
import shutil
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = LAB_DIR / "src" / "ingestion.py"
SAMPLE_DIR = LAB_DIR / "sample"


spec = importlib.util.spec_from_file_location(
    "lab02_ingestion",
    MODULE_PATH,
)

if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load ingestion module from {MODULE_PATH}")

ingestion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingestion)


VALID_FILE = SAMPLE_DIR / "customers_20260925_batch001.csv"


def test_valid_filename():
    assert ingestion.filename_is_valid(VALID_FILE)


def test_invalid_filename():
    assert not ingestion.filename_is_valid("customers-latest.csv")


def test_completion_marker_exists():
    assert ingestion.delivery_is_complete(VALID_FILE)


def test_checksum_is_valid():
    assert ingestion.checksum_is_valid(VALID_FILE)


def test_modified_file_fails_checksum(tmp_path):
    copied_file = tmp_path / VALID_FILE.name
    copied_checksum = tmp_path / f"{VALID_FILE.name}.sha256"

    shutil.copyfile(VALID_FILE, copied_file)
    shutil.copyfile(
        SAMPLE_DIR / f"{VALID_FILE.name}.sha256",
        copied_checksum,
    )

    with copied_file.open("a", encoding="utf-8") as handle:
        handle.write(
            "CUST999,changed@example.com,DK,true,2026-09-25T10:00:00Z\n"
        )

    assert not ingestion.checksum_is_valid(copied_file)


SCHEMA_FILE = LAB_DIR / "schemas" / "customers.schema.json"
INVALID_FILE = SAMPLE_DIR / "customers_20260925_batch002.csv"


def test_valid_csv_passes_schema_validation():
    schema = ingestion.load_schema(SCHEMA_FILE)

    assert ingestion.validate_csv(VALID_FILE, schema) == []


def test_invalid_csv_returns_validation_errors():
    schema = ingestion.load_schema(SCHEMA_FILE)

    errors = ingestion.validate_csv(INVALID_FILE, schema)

    reasons = {error["reason"] for error in errors}

    assert "invalid_email" in reasons
    assert "required_value_missing" in reasons
    assert "invalid_boolean" in reasons
    assert "invalid_timestamp" in reasons


def test_valid_delivery_is_validated():
    schema = ingestion.load_schema(SCHEMA_FILE)

    result = ingestion.evaluate_delivery(VALID_FILE, schema)

    assert result["status"] == "validated"
    assert result["reason"] == "all_checks_passed"
    assert len(result["sha256"]) == 64


def test_invalid_delivery_is_quarantined():
    schema = ingestion.load_schema(SCHEMA_FILE)

    result = ingestion.evaluate_delivery(INVALID_FILE, schema)

    assert result["status"] == "quarantined"
    assert result["reason"] == "schema_validation_failed"
    assert result["errors"]


def test_incomplete_delivery_is_deferred(tmp_path):
    schema = ingestion.load_schema(SCHEMA_FILE)

    data_file = tmp_path / "customers_20260925_batch003.csv"
    checksum_file = tmp_path / "customers_20260925_batch003.csv.sha256"

    shutil.copyfile(VALID_FILE, data_file)

    checksum = ingestion.calculate_sha256(data_file)
    checksum_file.write_text(
        f"{checksum}  {data_file.name}\n",
        encoding="utf-8",
    )

    result = ingestion.evaluate_delivery(data_file, schema)

    assert result == {
        "status": "deferred",
        "reason": "delivery_not_complete",
    }


def test_placeholder_for_s3_module():
    # S3-specific tests live in test_s3_delivery.py.
    assert True
