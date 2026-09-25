import hashlib
import re
from pathlib import Path


FILENAME_PATTERN = re.compile(
    r"^customers_[0-9]{8}_batch[0-9]{3}\.csv$"
)


def filename_is_valid(path):
    """Return True when the delivered filename follows the expected convention."""
    return bool(FILENAME_PATTERN.fullmatch(Path(path).name))


def completion_marker_path(path):
    """Return the expected completion-marker path for a data file."""
    data_path = Path(path)
    return data_path.with_name(data_path.name + ".complete")


def checksum_file_path(path):
    """Return the expected checksum sidecar path for a data file."""
    data_path = Path(path)
    return data_path.with_name(data_path.name + ".sha256")


def delivery_is_complete(path):
    """A delivery is complete only when its marker exists."""
    return completion_marker_path(path).is_file()


def calculate_sha256(path):
    """Calculate the SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def read_expected_sha256(path):
    """Read the expected digest from the .sha256 sidecar file."""
    checksum_path = checksum_file_path(path)

    content = checksum_path.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError("checksum file is empty")

    expected = content.split()[0].lower()

    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("checksum file does not contain a valid SHA-256 digest")

    return expected


def checksum_is_valid(path):
    """Compare the delivered file with its expected SHA-256 checksum."""
    return calculate_sha256(path) == read_expected_sha256(path)


def load_schema(path):
    """Load a JSON schema definition used by this practice lab."""
    import json

    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_csv(path, schema):
    """Validate CSV structure and basic field values."""
    import csv
    from datetime import datetime

    errors = []
    data_path = Path(path)

    with data_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)

        expected_columns = schema["required_columns"]
        actual_columns = reader.fieldnames or []

        if actual_columns != expected_columns:
            errors.append(
                {
                    "reason": "invalid_columns",
                    "expected": expected_columns,
                    "actual": actual_columns,
                }
            )
            return errors

        for row_number, row in enumerate(reader, start=2):
            customer_id = row["customer_id"].strip()
            email = row["email"].strip()
            consent = row["consent"].strip().lower()
            updated_at = row["updated_at"].strip()

            if not customer_id:
                errors.append(
                    {
                        "row": row_number,
                        "field": "customer_id",
                        "reason": "required_value_missing",
                    }
                )

            if "@" not in email or email.startswith("@") or email.endswith("@"):
                errors.append(
                    {
                        "row": row_number,
                        "field": "email",
                        "reason": "invalid_email",
                    }
                )

            if consent not in {"true", "false"}:
                errors.append(
                    {
                        "row": row_number,
                        "field": "consent",
                        "reason": "invalid_boolean",
                    }
                )

            try:
                datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            except ValueError:
                errors.append(
                    {
                        "row": row_number,
                        "field": "updated_at",
                        "reason": "invalid_timestamp",
                    }
                )

    return errors


def evaluate_delivery(path, schema):
    """Evaluate one delivered file and return its processing decision."""
    data_path = Path(path)

    if not filename_is_valid(data_path):
        return {
            "status": "quarantined",
            "reason": "invalid_filename",
        }

    if not delivery_is_complete(data_path):
        return {
            "status": "deferred",
            "reason": "delivery_not_complete",
        }

    checksum_path = checksum_file_path(data_path)

    if not checksum_path.is_file():
        return {
            "status": "quarantined",
            "reason": "checksum_file_missing",
        }

    try:
        checksum_valid = checksum_is_valid(data_path)
    except ValueError as error:
        return {
            "status": "quarantined",
            "reason": "invalid_checksum_file",
            "detail": str(error),
        }

    if not checksum_valid:
        return {
            "status": "quarantined",
            "reason": "checksum_mismatch",
        }

    validation_errors = validate_csv(data_path, schema)

    if validation_errors:
        return {
            "status": "quarantined",
            "reason": "schema_validation_failed",
            "errors": validation_errors,
        }

    return {
        "status": "validated",
        "reason": "all_checks_passed",
        "sha256": calculate_sha256(data_path),
    }
