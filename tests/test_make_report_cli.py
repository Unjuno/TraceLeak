import json
import subprocess
import sys


def sample_input() -> dict:
    return {
        "target": "synthetic-example",
        "view": "redacted",
        "metric": "DeltaH",
        "full_score": 10.0,
        "groups": {
            "example_branch_event": {
                "ablated_score": 4.0,
                "group_type": "branch",
                "location": "examples/synthetic/target.c:21",
            }
        },
        "notes": ["synthetic sample"],
    }


def test_make_report_cli_writes_markdown(tmp_path) -> None:
    input_path = tmp_path / "ablation.json"
    output_path = tmp_path / "report.md"
    input_path.write_text(json.dumps(sample_input()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_report.py",
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
    assert "TraceLeak Attribution Report" in output_path.read_text(encoding="utf-8")


def test_make_report_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "ablation.json"
    output_path = tmp_path / "report.json"
    input_path.write_text(json.dumps(sample_input()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_report.py",
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
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["target"] == "synthetic-example"


def test_make_report_cli_reports_missing_input(tmp_path) -> None:
    missing_path = tmp_path / "missing.json"
    output_path = tmp_path / "report.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_report.py",
            "--in",
            str(missing_path),
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "input file not found" in result.stderr
