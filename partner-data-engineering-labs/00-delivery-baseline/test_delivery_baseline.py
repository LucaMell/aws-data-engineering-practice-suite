from pathlib import Path


LAB_DIR = Path(__file__).parent
REPOSITORY_ROOT = LAB_DIR.parents[1]

REQUIRED_DOCUMENTS = {
    LAB_DIR / "README.md": "# Lab 00:",
    LAB_DIR / "docs" / "partner-pipeline-checklist.md": "# Partner Pipeline",
    LAB_DIR / "docs" / "field-mapping-template.md": "# Source-to-Target",
    LAB_DIR / "docs" / "data-dictionary-template.md": "# Data Dictionary",
    LAB_DIR / "docs" / "data-contract-template.md": "# Partner Data Contract",
    LAB_DIR / "docs" / "runbook-template.md": "# Pipeline Operations Runbook",
    REPOSITORY_ROOT / ".github" / "pull_request_template.md": "# Change summary",
}


def test_required_documents_exist():
    missing = [
        str(path.relative_to(REPOSITORY_ROOT))
        for path in REQUIRED_DOCUMENTS
        if not path.is_file()
    ]

    assert not missing, f"Missing required documents: {missing}"


def test_documents_have_expected_headings():
    for path, expected_heading in REQUIRED_DOCUMENTS.items():
        content = path.read_text(encoding="utf-8")

        assert expected_heading in content, (
            f"{path.relative_to(REPOSITORY_ROOT)} "
            f"is missing heading: {expected_heading}"
        )


def test_delivery_topics_are_documented():
    combined_content = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in REQUIRED_DOCUMENTS
    )

    required_topics = {
        "schema",
        "quality",
        "security",
        "replay",
        "cost",
        "owner",
    }

    missing_topics = {
        topic
        for topic in required_topics
        if topic not in combined_content
    }

    assert not missing_topics, (
        f"Lab 00 documentation is missing topics: {missing_topics}"
    )
