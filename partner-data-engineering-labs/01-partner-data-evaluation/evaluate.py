import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


VALID_COUNTRIES = {"DK", "SE", "NO", "DE", "GB", "FR", "NL", "IT"}
VALID_STATUSES = {"active", "inactive"}
VALID_CONSENT_VALUES = {"true", "false"}
VALID_EVENT_TYPES = {"page_view", "purchase", "email_open", "email_click"}
VALID_EVENT_SOURCES = {"web", "email", "store"}

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_timestamp(value):
    if not value:
        return False

    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return False

    return True


def normalized_strings(record):
    return {
        key: value.strip() if isinstance(value, str) else value
        for key, value in record.items()
    }


def profile_records(records):
    columns = sorted(
        {
            key
            for record in records
            for key in record
        }
    )

    null_counts = {
        column: sum(
            record.get(column) in (None, "")
            for record in records
        )
        for column in columns
    }

    distinct_counts = {
        column: len(
            {
                str(record.get(column))
                for record in records
                if record.get(column) not in (None, "")
            }
        )
        for column in columns
    }

    return {
        "columns": columns,
        "null_counts": null_counts,
        "distinct_counts": distinct_counts,
    }


def rejection_counts(rejected_records):
    return dict(
        sorted(
            Counter(
                reason
                for rejected in rejected_records
                for reason in rejected["error_codes"]
            ).items()
        )
    )


def read_customers(path):
    all_records = []
    accepted = []
    rejected = []
    seen_customer_ids = set()

    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)

        for line_number, source_record in enumerate(reader, start=2):
            record = normalized_strings(source_record)
            record["email"] = record.get("email", "").lower()
            record["status"] = record.get("status", "").lower()
            record["marketing_consent"] = record.get(
                "marketing_consent",
                "",
            ).lower()

            reasons = []
            customer_id = record.get("customer_id", "")
            email = record.get("email", "")
            lifetime_value = record.get("lifetime_value", "")

            if not customer_id:
                reasons.append("MISSING_CUSTOMER_ID")
            elif customer_id in seen_customer_ids:
                reasons.append("DUPLICATE_CUSTOMER_ID")
            else:
                seen_customer_ids.add(customer_id)

            if not EMAIL_PATTERN.fullmatch(email):
                reasons.append("INVALID_EMAIL")

            if record.get("country_code") not in VALID_COUNTRIES:
                reasons.append("INVALID_COUNTRY_CODE")

            if record.get("status") not in VALID_STATUSES:
                reasons.append("INVALID_STATUS")

            if (
                record.get("marketing_consent")
                not in VALID_CONSENT_VALUES
            ):
                reasons.append("INVALID_MARKETING_CONSENT")

            if not is_valid_timestamp(record.get("signup_timestamp")):
                reasons.append("INVALID_SIGNUP_TIMESTAMP")

            try:
                record["lifetime_value"] = float(lifetime_value)
            except (TypeError, ValueError):
                reasons.append("INVALID_LIFETIME_VALUE")
            else:
                if record["lifetime_value"] < 0:
                    reasons.append("NEGATIVE_LIFETIME_VALUE")

            all_records.append(record)

            if reasons:
                rejected.append(
                    {
                        "line_number": line_number,
                        "error_codes": reasons,
                        "record": record,
                    }
                )
            else:
                accepted.append(record)

    return all_records, accepted, rejected


def read_events(path, valid_customer_ids):
    total_lines = 0
    all_records = []
    accepted = []
    rejected = []
    seen_event_ids = set()

    with path.open(encoding="utf-8") as source:
        for line_number, raw_line in enumerate(source, start=1):
            total_lines += 1

            try:
                source_record = json.loads(raw_line)
            except json.JSONDecodeError:
                rejected.append(
                    {
                        "line_number": line_number,
                        "error_codes": ["MALFORMED_JSON"],
                        "record": None,
                    }
                )
                continue

            if not isinstance(source_record, dict):
                rejected.append(
                    {
                        "line_number": line_number,
                        "error_codes": ["EVENT_NOT_AN_OBJECT"],
                        "record": None,
                    }
                )
                continue

            record = normalized_strings(source_record)
            record["event_type"] = str(
                record.get("event_type", "")
            ).lower()
            record["source"] = str(
                record.get("source", "")
            ).lower()

            all_records.append(record)
            reasons = []

            event_id = record.get("event_id", "")
            customer_id = record.get("customer_id", "")
            event_type = record.get("event_type", "")
            amount = record.get("amount")

            if not event_id:
                reasons.append("MISSING_EVENT_ID")
            elif event_id in seen_event_ids:
                reasons.append("DUPLICATE_EVENT_ID")
            else:
                seen_event_ids.add(event_id)

            if not customer_id:
                reasons.append("MISSING_EVENT_CUSTOMER_ID")
            elif customer_id not in valid_customer_ids:
                reasons.append("ORPHAN_CUSTOMER_ID")

            if event_type not in VALID_EVENT_TYPES:
                reasons.append("INVALID_EVENT_TYPE")

            if not is_valid_timestamp(
                record.get("event_timestamp")
            ):
                reasons.append("INVALID_EVENT_TIMESTAMP")

            if record.get("source") not in VALID_EVENT_SOURCES:
                reasons.append("INVALID_EVENT_SOURCE")

            if event_type == "purchase":
                if (
                    isinstance(amount, bool)
                    or not isinstance(amount, (int, float))
                ):
                    reasons.append("INVALID_PURCHASE_AMOUNT")
                elif amount < 0:
                    reasons.append("NEGATIVE_PURCHASE_AMOUNT")

            if reasons:
                rejected.append(
                    {
                        "line_number": line_number,
                        "error_codes": reasons,
                        "record": record,
                    }
                )
            else:
                accepted.append(record)

    return total_lines, all_records, accepted, rejected


def write_json_lines(path, records):
    with path.open("w", encoding="utf-8") as destination:
        for record in records:
            destination.write(
                json.dumps(record, sort_keys=True) + "\n"
            )


def evaluate(customers_path, events_path, output_dir):
    customer_records, accepted_customers, rejected_customers = (
        read_customers(customers_path)
    )

    valid_customer_ids = {
        record["customer_id"]
        for record in accepted_customers
    }

    (
        event_line_count,
        event_records,
        accepted_events,
        rejected_events,
    ) = read_events(events_path, valid_customer_ids)

    referenced_customer_ids = [
        record.get("customer_id")
        for record in event_records
        if record.get("customer_id")
    ]

    matched_references = [
        customer_id
        for customer_id in referenced_customer_ids
        if customer_id in valid_customer_ids
    ]

    customers_with_activity = (
        set(referenced_customer_ids) & valid_customer_ids
    )

    if not accepted_customers or not accepted_events:
        recommendation = "stop"
    elif rejected_customers or rejected_events:
        recommendation = "proceed_with_conditions"
    else:
        recommendation = "proceed"

    customer_profile = profile_records(customer_records)
    event_profile = profile_records(event_records)

    report = {
        "customers": {
            "input_records": len(customer_records),
            "accepted_records": len(accepted_customers),
            "rejected_records": len(rejected_customers),
            "rejection_counts": rejection_counts(
                rejected_customers
            ),
            **customer_profile,
        },
        "events": {
            "input_lines": event_line_count,
            "parsed_records": len(event_records),
            "accepted_records": len(accepted_events),
            "rejected_records": len(rejected_events),
            "rejection_counts": rejection_counts(
                rejected_events
            ),
            **event_profile,
        },
        "coverage": {
            "valid_customers": len(valid_customer_ids),
            "customers_with_activity": len(
                customers_with_activity
            ),
            "customer_activity_rate_percent": round(
                (
                    len(customers_with_activity)
                    / len(valid_customer_ids)
                    * 100
                )
                if valid_customer_ids
                else 0,
                2,
            ),
            "event_customer_match_rate_percent": round(
                (
                    len(matched_references)
                    / len(referenced_customer_ids)
                    * 100
                )
                if referenced_customer_ids
                else 0,
                2,
            ),
        },
        "reconciliation": {
            "customers_balance": (
                len(customer_records)
                == len(accepted_customers)
                + len(rejected_customers)
            ),
            "events_balance": (
                event_line_count
                == len(accepted_events)
                + len(rejected_events)
            ),
        },
        "recommendation": recommendation,
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    write_json_lines(
        output_dir / "accepted_customers.jsonl",
        accepted_customers,
    )
    write_json_lines(
        output_dir / "rejected_customers.jsonl",
        rejected_customers,
    )
    write_json_lines(
        output_dir / "accepted_events.jsonl",
        accepted_events,
    )
    write_json_lines(
        output_dir / "rejected_events.jsonl",
        rejected_events,
    )

    (output_dir / "profile.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return report


def main():
    lab_directory = Path(__file__).parent

    parser = argparse.ArgumentParser(
        description="Evaluate synthetic partner datasets."
    )
    parser.add_argument(
        "--customers",
        type=Path,
        default=lab_directory
        / "sample"
        / "partner_customers.csv",
    )
    parser.add_argument(
        "--events",
        type=Path,
        default=lab_directory
        / "sample"
        / "partner_events.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=lab_directory / "output",
    )
    arguments = parser.parse_args()

    report = evaluate(
        customers_path=arguments.customers,
        events_path=arguments.events,
        output_dir=arguments.output,
    )

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
