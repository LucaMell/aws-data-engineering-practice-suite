import argparse
import csv
import json
from pathlib import Path

import duckdb

from evaluate import evaluate


RESULT_VIEWS = [
    "customer_country_summary",
    "event_type_summary",
    "customer_activity_summary",
    "rejection_reason_summary",
    "pipeline_reconciliation",
]


def load_accepted_table(connection, table_name, path):
    escaped_path = path.as_posix().replace("'", "''")

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM read_json_auto(
            '{escaped_path}',
            format = 'newline_delimited'
        )
        """
    )


def load_rejection_table(connection, table_name, path):
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name} (
            line_number INTEGER,
            error_codes VARCHAR[]
        )
        """
    )

    rows = []

    with path.open(encoding="utf-8") as source:
        for line in source:
            rejected = json.loads(line)
            rows.append(
                (
                    rejected["line_number"],
                    rejected["error_codes"],
                )
            )

    connection.executemany(
        f"INSERT INTO {table_name} VALUES (?, ?)",
        rows,
    )


def export_view(connection, view_name, destination):
    cursor = connection.execute(
        f"SELECT * FROM {view_name}"
    )

    columns = [
        description[0]
        for description in cursor.description
    ]
    rows = cursor.fetchall()

    with destination.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as output:
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def run_sql_checks(
    customers_path,
    events_path,
    sql_path,
    output_dir,
):
    profile = evaluate(
        customers_path=customers_path,
        events_path=events_path,
        output_dir=output_dir,
    )

    connection = duckdb.connect(":memory:")

    try:
        load_accepted_table(
            connection,
            "accepted_customers",
            output_dir / "accepted_customers.jsonl",
        )
        load_accepted_table(
            connection,
            "accepted_events",
            output_dir / "accepted_events.jsonl",
        )
        load_rejection_table(
            connection,
            "rejected_customers",
            output_dir / "rejected_customers.jsonl",
        )
        load_rejection_table(
            connection,
            "rejected_events",
            output_dir / "rejected_events.jsonl",
        )

        connection.execute(
            """
            CREATE TABLE source_counts (
                dataset VARCHAR,
                input_count INTEGER
            )
            """
        )
        connection.executemany(
            "INSERT INTO source_counts VALUES (?, ?)",
            [
                (
                    "customers",
                    profile["customers"]["input_records"],
                ),
                (
                    "events",
                    profile["events"]["input_lines"],
                ),
            ],
        )

        connection.execute(
            sql_path.read_text(encoding="utf-8")
        )

        sql_output_dir = output_dir / "sql"
        sql_output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        view_results = {
            view_name: export_view(
                connection,
                view_name,
                sql_output_dir / f"{view_name}.csv",
            )
            for view_name in RESULT_VIEWS
        }
    finally:
        connection.close()

    summary = {
        "exported_row_counts": {
            view_name: len(rows)
            for view_name, rows in view_results.items()
        },
        "pipeline_reconciliation": view_results[
            "pipeline_reconciliation"
        ],
    }

    (output_dir / "sql_summary.json").write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    return summary


def main():
    lab_directory = Path(__file__).parent

    parser = argparse.ArgumentParser(
        description="Run local DuckDB quality checks."
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
        "--sql",
        type=Path,
        default=lab_directory / "quality.sql",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=lab_directory / "output",
    )
    arguments = parser.parse_args()

    summary = run_sql_checks(
        customers_path=arguments.customers,
        events_path=arguments.events,
        sql_path=arguments.sql,
        output_dir=arguments.output,
    )

    print(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
