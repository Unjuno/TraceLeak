import json
import subprocess
import sys


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
    }


def test_comparison_to_report_cli_writes_markdown(tmp_path) -> None:
    input_path = tmp_path / "comparison.json"
    output_path = tmp_path / "comparison_report.md"
    input_path.write_text(json.dumps(comparison_input()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/comparison_to_report.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "TraceLeak Comparison Report" in output_path.read_text(encoding="utf-8")


def test_comparison_to_report_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "comparison.json"
    output_path = tmp_path / "comparison_report.json"
    input_path.write_text(json.dumps(comparison_input()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/comparison_to_report.py",
            "--in",
            str(input_path),
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
    assert payload["report_type"] == "comparison"
    assert payload["status"] == "higher"


def test_comparison_to_report_cli_rejects_invalid_input(tmp_path) -> None:
    input_path = tmp_path / "comparison.json"
    output_path = tmp_path / "comparison_report.md"
    data = comparison_input()
    data["delta"] = 99.0
    input_path.write_text(json.dumps(data), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/comparison_to_report.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "delta does not match" in result.stderr
