import importlib.util
from pathlib import Path


LAB_DIR = Path(__file__).parents[1]
MODULE_PATH = LAB_DIR / "evaluate.py"

MODULE_SPEC = importlib.util.spec_from_file_location(
    "partner_data_evaluator",
    MODULE_PATH,
)

if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise ImportError(f"Cannot load evaluator from {MODULE_PATH}")

evaluator = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(evaluator)


def run_sample_evaluation(tmp_path):
    return evaluator.evaluate(
        customers_path=LAB_DIR
        / "sample"
        / "partner_customers.csv",
        events_path=LAB_DIR
        / "sample"
        / "partner_events.jsonl",
        output_dir=tmp_path,
    )


def test_expected_evaluation_summary(tmp_path):
    report = run_sample_evaluation(tmp_path)

    assert report["customers"]["input_records"] == 12
    assert report["customers"]["accepted_records"] == 4
    assert report["customers"]["rejected_records"] == 8

    assert report["events"]["input_lines"] == 13
    assert report["events"]["parsed_records"] == 12
    assert report["events"]["accepted_records"] == 5
    assert report["events"]["rejected_records"] == 8

    assert report["reconciliation"] == {
        "customers_balance": True,
        "events_balance": True,
    }

    assert report["recommendation"] == (
        "proceed_with_conditions"
    )


def test_customer_normalization_and_rejections():
    all_records, accepted, rejected = evaluator.read_customers(
        LAB_DIR / "sample" / "partner_customers.csv"
    )

    accepted_by_id = {
        record["customer_id"]: record
        for record in accepted
    }

    assert len(all_records) == 12
    assert accepted_by_id["c-1001"]["email"] == (
        "alice.one@example.com"
    )
    assert accepted_by_id["c-1004"]["email"] == (
        "dana.four@example.com"
    )

    assert evaluator.rejection_counts(rejected) == {
        "DUPLICATE_CUSTOMER_ID": 1,
        "INVALID_COUNTRY_CODE": 1,
        "INVALID_EMAIL": 2,
        "INVALID_MARKETING_CONSENT": 1,
        "INVALID_SIGNUP_TIMESTAMP": 1,
        "INVALID_STATUS": 1,
        "MISSING_CUSTOMER_ID": 1,
        "NEGATIVE_LIFETIME_VALUE": 1,
    }


def test_event_rejection_reasons():
    _, accepted_customers, _ = evaluator.read_customers(
        LAB_DIR / "sample" / "partner_customers.csv"
    )
    valid_customer_ids = {
        record["customer_id"]
        for record in accepted_customers
    }

    total_lines, parsed, accepted, rejected = (
        evaluator.read_events(
            LAB_DIR / "sample" / "partner_events.jsonl",
            valid_customer_ids,
        )
    )

    assert total_lines == 13
    assert len(parsed) == 12
    assert len(accepted) == 5

    assert evaluator.rejection_counts(rejected) == {
        "DUPLICATE_EVENT_ID": 1,
        "INVALID_EVENT_SOURCE": 1,
        "INVALID_EVENT_TIMESTAMP": 1,
        "INVALID_EVENT_TYPE": 1,
        "INVALID_PURCHASE_AMOUNT": 1,
        "MALFORMED_JSON": 1,
        "MISSING_EVENT_CUSTOMER_ID": 1,
        "MISSING_EVENT_ID": 1,
        "ORPHAN_CUSTOMER_ID": 3,
    }


def test_coverage_metrics(tmp_path):
    report = run_sample_evaluation(tmp_path)

    assert report["coverage"] == {
        "valid_customers": 4,
        "customers_with_activity": 4,
        "customer_activity_rate_percent": 100.0,
        "event_customer_match_rate_percent": 72.73,
    }


def test_output_files_are_created(tmp_path):
    run_sample_evaluation(tmp_path)

    expected_files = {
        "accepted_customers.jsonl",
        "rejected_customers.jsonl",
        "accepted_events.jsonl",
        "rejected_events.jsonl",
        "profile.json",
    }

    assert {
        path.name
        for path in tmp_path.iterdir()
    } == expected_files


import csv
import json
import subprocess
import sys


RUNNER_PATH = LAB_DIR / "run_sql_checks.py"


def run_sql_runner(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--output",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return json.loads(completed.stdout)


def read_csv_rows(path):
    with path.open(
        newline="",
        encoding="utf-8",
    ) as source:
        return list(csv.DictReader(source))


def test_sql_pipeline_reconciliation(tmp_path):
    summary = run_sql_runner(tmp_path)

    reconciliation = {
        row["dataset"]: row
        for row in summary["pipeline_reconciliation"]
    }

    assert reconciliation["customers"] == {
        "dataset": "customers",
        "input_count": 12,
        "accepted_count": 4,
        "rejected_count": 8,
        "processed_count": 12,
        "reconciles": True,
    }

    assert reconciliation["events"] == {
        "dataset": "events",
        "input_count": 13,
        "accepted_count": 5,
        "rejected_count": 8,
        "processed_count": 13,
        "reconciles": True,
    }


def test_sql_report_files_are_created(tmp_path):
    summary = run_sql_runner(tmp_path)

    expected_views = {
        "customer_country_summary",
        "event_type_summary",
        "customer_activity_summary",
        "rejection_reason_summary",
        "pipeline_reconciliation",
    }

    assert set(
        summary["exported_row_counts"]
    ) == expected_views

    assert {
        path.stem
        for path in (tmp_path / "sql").glob("*.csv")
    } == expected_views


def test_sql_customer_activity_results(tmp_path):
    run_sql_runner(tmp_path)

    rows = read_csv_rows(
        tmp_path
        / "sql"
        / "customer_activity_summary.csv"
    )
    rows_by_customer = {
        row["customer_id"]: row
        for row in rows
    }

    assert rows_by_customer["c-1001"]["event_count"] == "2"
    assert rows_by_customer["c-1001"]["purchase_count"] == "1"
    assert float(
        rows_by_customer["c-1001"]["purchase_amount"]
    ) == 49.95

    assert rows_by_customer["c-1004"]["event_count"] == "1"


REQUIRED_LAB_DOCUMENTS = {
    LAB_DIR / "README.md": [
        "## Business scenario",
        "## Definition of done",
    ],
    LAB_DIR / "docs" / "evaluation-report.md": [
        "Proceed with conditions",
        "| Customers | 12 | 4 | 8 | Yes |",
        "| Events | 13 | 5 | 8 | Yes |",
        "72.73%",
    ],
    LAB_DIR / "docs" / "field-mapping.md": [
        "## Customer mappings",
        "## Event mappings",
        "## Reconciliation",
    ],
    LAB_DIR / "docs" / "data-dictionary.md": [
        "## Dataset: validated_customers",
        "## Dataset: validated_events",
        "## Dataset: rejected_records",
    ],
}


def test_lab_documentation_exists():
    missing = [
        str(path.relative_to(LAB_DIR))
        for path in REQUIRED_LAB_DOCUMENTS
        if not path.is_file()
    ]

    assert not missing, f"Missing Lab 01 documents: {missing}"


def test_lab_documentation_contains_required_evidence():
    for path, expected_fragments in (
        REQUIRED_LAB_DOCUMENTS.items()
    ):
        content = path.read_text(encoding="utf-8")

        missing_fragments = [
            fragment
            for fragment in expected_fragments
            if fragment not in content
        ]

        assert not missing_fragments, (
            f"{path.relative_to(LAB_DIR)} is missing: "
            f"{missing_fragments}"
        )
