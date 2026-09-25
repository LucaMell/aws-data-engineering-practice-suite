import re
from pathlib import Path


DELIVERY_PATTERN = re.compile(
    r"^customers_(?P<date>[0-9]{8})_batch[0-9]{3}\.csv$"
)


def build_landing_key(filename):
    """Build the landing object key from a valid delivery filename."""
    match = DELIVERY_PATTERN.fullmatch(Path(filename).name)

    if not match:
        raise ValueError("invalid delivery filename")

    delivery_date = match.group("date")

    year = delivery_date[0:4]
    month = delivery_date[4:6]
    day = delivery_date[6:8]

    return (
        f"landing/customers/{year}/{month}/{day}/"
        f"{Path(filename).name}"
    )


def upload_delivery(s3, bucket, data_path):
    """Upload the data file and its delivery sidecars to landing/."""
    data_path = Path(data_path)

    base_key = build_landing_key(data_path.name)

    objects = [
        (data_path, base_key),
        (
            data_path.with_name(data_path.name + ".sha256"),
            base_key + ".sha256",
        ),
        (
            data_path.with_name(data_path.name + ".complete"),
            base_key + ".complete",
        ),
    ]

    for local_path, object_key in objects:
        if not local_path.is_file():
            raise FileNotFoundError(local_path)

        s3.upload_file(
            str(local_path),
            bucket,
            object_key,
        )

    return [object_key for _, object_key in objects]


def read_local_checksum(data_path):
    """Read the SHA-256 value declared by the local checksum sidecar."""
    data_path = Path(data_path)
    checksum_path = data_path.with_name(data_path.name + ".sha256")

    content = checksum_path.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError("checksum file is empty")

    return content.split()[0].lower()


def existing_delivery_checksum(s3, bucket, data_path):
    """Return the checksum already stored for this delivery, if it exists."""
    base_key = build_landing_key(Path(data_path).name)
    checksum_key = base_key + ".sha256"

    try:
        response = s3.get_object(
            Bucket=bucket,
            Key=checksum_key,
        )
    except s3.exceptions.NoSuchKey:
        return None

    content = response["Body"].read().decode("utf-8").strip()

    if not content:
        raise ValueError("stored checksum file is empty")

    return content.split()[0].lower()


def classify_delivery(s3, bucket, data_path):
    """Classify a delivery as new, duplicate, or conflicting."""
    local_checksum = read_local_checksum(data_path)

    existing_checksum = existing_delivery_checksum(
        s3,
        bucket,
        data_path,
    )

    if existing_checksum is None:
        return "new"

    if existing_checksum == local_checksum:
        return "duplicate"

    return "conflict"


def ingest_delivery(s3, bucket, data_path):
    """Upload only a genuinely new delivery."""
    classification = classify_delivery(
        s3,
        bucket,
        data_path,
    )

    if classification == "duplicate":
        return {
            "status": "duplicate",
            "uploaded_keys": [],
        }

    if classification == "conflict":
        return {
            "status": "conflict",
            "uploaded_keys": [],
        }

    uploaded_keys = upload_delivery(
        s3,
        bucket,
        data_path,
    )

    return {
        "status": "uploaded",
        "uploaded_keys": uploaded_keys,
    }


ALLOWED_STAGES = {
    "landing",
    "validated",
    "quarantined",
    "archived",
    "curated",
}


def build_stage_key(stage, filename):
    """Build an object key for one supported ingestion stage."""
    if stage not in ALLOWED_STAGES:
        raise ValueError(f"unsupported stage: {stage}")

    match = DELIVERY_PATTERN.fullmatch(Path(filename).name)

    if not match:
        raise ValueError("invalid delivery filename")

    delivery_date = match.group("date")

    year = delivery_date[0:4]
    month = delivery_date[4:6]
    day = delivery_date[6:8]

    return (
        f"{stage}/customers/{year}/{month}/{day}/"
        f"{Path(filename).name}"
    )


def copy_delivery_to_stage(s3, bucket, filename, stage):
    """Copy a delivered data object from landing/ into another stage."""
    source_key = build_stage_key("landing", filename)
    destination_key = build_stage_key(stage, filename)

    s3.copy_object(
        Bucket=bucket,
        CopySource={
            "Bucket": bucket,
            "Key": source_key,
        },
        Key=destination_key,
    )

    return destination_key


def route_delivery(s3, bucket, filename, evaluation):
    """Route a landed delivery according to its validation decision."""
    status = evaluation["status"]

    if status == "validated":
        return {
            "status": "validated",
            "destination_key": copy_delivery_to_stage(
                s3,
                bucket,
                filename,
                "validated",
            ),
        }

    if status == "quarantined":
        return {
            "status": "quarantined",
            "destination_key": copy_delivery_to_stage(
                s3,
                bucket,
                filename,
                "quarantined",
            ),
        }

    if status == "deferred":
        return {
            "status": "deferred",
            "destination_key": None,
        }

    raise ValueError(f"unsupported evaluation status: {status}")


def archive_delivery(s3, bucket, filename):
    """Copy a successful original delivery into the archive prefix."""
    return copy_delivery_to_stage(
        s3,
        bucket,
        filename,
        "archived",
    )


def copy_between_stages(s3, bucket, filename, source_stage, destination_stage):
    """Copy one data object between supported ingestion stages."""
    source_key = build_stage_key(source_stage, filename)
    destination_key = build_stage_key(destination_stage, filename)

    s3.copy_object(
        Bucket=bucket,
        CopySource={
            "Bucket": bucket,
            "Key": source_key,
        },
        Key=destination_key,
    )

    return destination_key
