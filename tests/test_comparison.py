import json

import pytest

from traceleak.comparison import (
    ComparisonError,
    classify_comparison,
    comparison_delta,
    comparison_report_dict,
    comparison_report_markdown,
    validate_comparison,
    write_comparison_report_json,
    write_comparison_report_markdown,
)


def comparison_input() -> dict:
    return {
        "comparison_id": "synthetic_leak_control_0001",
        "comparison_type": "leak_vs_control",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "left": {"label": "leak", "score": 4.0, "report": "leak.md"},
        "right": {"label": "control", "score": 0.2, "report": "control.md"},
        "delta": 3.8,
        "status": "higher",
        "interpretation": "Leak is higher than control.",
        "notes": ["sample note"],
    }


def test_comparison_delta_and_classification() -> None:
    assert comparison_delta(4.0, 0.2) == pytest.approx(3.8)
    assert classify_comparison(3.8) == "higher"
    assert classify_comparison(-3.8) == "lower"
    assert classify_comparison(0.0) == "unchanged"


def test_validate_comparison_accepts_valid_input() -> None:
    validate_comparison(comparison_input())


def test_validate_comparison_rejects_delta_mismatch() -> None:
    data = comparison_input()
    data["delta"] = 9.0
    with pytest.raises(ComparisonError):
        validate_comparison(data)


def test_validate_comparison_rejects_raw_public_view() -> None:
    data = comparison_input()
    data["view"] = "raw"
    with pytest.raises(ComparisonError):
        validate_comparison(data)


def test_validate_comparison_rejects_secret_equivalent_field() -> None:
    data = comparison_input()
    data["private_key"] = "not allowed"
    with pytest.raises(ComparisonError):
        validate_comparison(data)


def test_comparison_report_dict() -> None:
    report = comparison_report_dict(comparison_input())
    assert report["report_type"] == "comparison"
    assert report["comparison_id"] == "synthetic_leak_control_0001"
    assert report["delta"] == pytest.approx(3.8)
    assert report["status"] == "higher"


def test_comparison_report_markdown_contains_expected_sections() -> None:
    report = comparison_report_dict(comparison_input())
    markdown = comparison_report_markdown(report)
    assert "# TraceLeak Comparison Report" in markdown
    assert "## Measurements" in markdown
    assert "leak" in markdown
    assert "control" in markdown
    assert "Leak is higher than control." in markdown


def test_write_comparison_report_json(tmp_path) -> None:
    report = comparison_report_dict(comparison_input())
    output_path = tmp_path / "comparison_report.json"
    write_comparison_report_json(output_path, report)
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["status"] == "higher"


def test_write_comparison_report_markdown(tmp_path) -> None:
    report = comparison_report_dict(comparison_input())
    output_path = tmp_path / "comparison_report.md"
    write_comparison_report_markdown(output_path, report)
    text = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Comparison Report" in text
    assert "leak.md" in text
    assert "control.md" in text
