from ingestion import evaluate_delivery
from s3_delivery import (
    archive_delivery,
    copy_between_stages,
    ingest_delivery,
    route_delivery,
)


def process_delivery(s3, bucket, data_path, schema):
    """Process one complete partner delivery from landing to its final stage."""

    landing_result = ingest_delivery(
        s3,
        bucket,
        data_path,
    )

    if landing_result["status"] in {"duplicate", "conflict"}:
        return {
            "status": landing_result["status"],
            "evaluation": None,
        }

    evaluation = evaluate_delivery(
        data_path,
        schema,
    )

    routing = route_delivery(
        s3,
        bucket,
        data_path.name,
        evaluation,
    )

    result = {
        "status": routing["status"],
        "evaluation": evaluation,
        "destination_key": routing["destination_key"],
    }

    if evaluation["status"] != "validated":
        return result

    result["archive_key"] = archive_delivery(
        s3,
        bucket,
        data_path.name,
    )

    result["curated_key"] = copy_between_stages(
        s3,
        bucket,
        data_path.name,
        "validated",
        "curated",
    )

    return result
