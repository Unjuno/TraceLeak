import json

from traceleak.patch_reporting import (
    patch_verification_report_dict,
    patch_verification_report_markdown,
    write_patch_verification_report_json,
    write_patch_verification_report_markdown,
)


def patch_result() -> dict:
    return {
        "verification_id": "synthetic_patch_0001",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "before": {"run_id": "before", "score": 4.0, "report": "before.md"},
        "after": {"run_id": "after", "score": 1.0, "report": "after.md"},
        "delta": 3.0,
        "status": "reduced",
        "changed_groups": [
            {
                "group_id": "synthetic_branch_event",
                "location": "examples/synthetic/target.py:19",
                "before_contribution": 3.0,
                "after_contribution": 0.5,
            }
        ],
        "notes": ["sample note"],
    }


def test_patch_verification_report_dict() -> None:
    report = patch_verification_report_dict(patch_result())
    assert report["report_type"] == "patch_verification"
    assert report["verification_id"] == "synthetic_patch_0001"
    assert report["delta"] == 3.0
    assert report["status"] == "reduced"
    assert report["changed_groups"][0]["group_id"] == "synthetic_branch_event"


def test_patch_verification_report_markdown_contains_expected_sections() -> None:
    report = patch_verification_report_dict(patch_result())
    markdown = patch_verification_report_markdown(report)
    assert "# TraceLeak Patch Verification Report" in markdown
    assert "## Before / After" in markdown
    assert "## Changed Groups" in markdown
    assert "synthetic_branch_event" in markdown
    assert "sample note" in markdown


def test_write_patch_verification_report_json(tmp_path) -> None:
    report = patch_verification_report_dict(patch_result())
    output_path = tmp_path / "patch_report.json"
    write_patch_verification_report_json(output_path, report)
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["status"] == "reduced"
    assert payload["delta"] == 3.0


def test_write_patch_verification_report_markdown(tmp_path) -> None:
    report = patch_verification_report_dict(patch_result())
    output_path = tmp_path / "patch_report.md"
    write_patch_verification_report_markdown(output_path, report)
    text = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Patch Verification Report" in text
    assert "before.md" in text
    assert "after.md" in text
