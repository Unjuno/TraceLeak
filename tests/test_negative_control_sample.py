import json
import subprocess
import sys

from traceleak.comparison import comparison_report_dict, load_comparison


def test_negative_control_sample_is_valid() -> None:
    data = load_comparison("examples/synthetic/negative_control_sample.json")
    report = comparison_report_dict(data)
    assert report["comparison_type"] == "negative_control"
    assert report["status"] == "unchanged"
    assert report["delta"] == 0.0


def test_negative_control_sample_renders_markdown(tmp_path) -> None:
    output_path = tmp_path / "negative_control_report.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/comparison_to_report.py",
            "--in",
            "examples/synthetic/negative_control_sample.json",
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = output_path.read_text(encoding="utf-8")
    assert "TraceLeak Comparison Report" in text
    assert "negative_control" in text
    assert "unchanged" in text


def test_negative_control_sample_renders_json(tmp_path) -> None:
    output_path = tmp_path / "negative_control_report.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/comparison_to_report.py",
            "--in",
            "examples/synthetic/negative_control_sample.json",
            "--out",
            str(output_path),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["comparison_type"] == "negative_control"
    assert payload["status"] == "unchanged"
