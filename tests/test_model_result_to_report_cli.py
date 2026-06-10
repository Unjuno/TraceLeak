import json
import subprocess
import sys


def model_result() -> dict:
    return {
        "experiment_id": "exp_001_synthetic_generated",
        "target": "synthetic-leak",
        "view": "redacted",
        "model": {"name": "placeholder", "type": "neural"},
        "metrics": {"test": {"DeltaH": 4.0, "accuracy": 0.875}},
        "attributions": [
            {
                "group_id": "synthetic_branch_event",
                "group_type": "branch",
                "score": 3.0,
                "location": "examples/synthetic/target.py:19",
                "evidence": ["model_importance"],
            }
        ],
    }


def test_model_result_to_report_cli_writes_markdown(tmp_path) -> None:
    input_path = tmp_path / "model_result.json"
    output_path = tmp_path / "model_report.md"
    input_path.write_text(json.dumps(model_result()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_result_to_report.py",
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
    assert "synthetic_branch_event" in output_path.read_text(encoding="utf-8")


def test_model_result_to_report_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "model_result.json"
    output_path = tmp_path / "model_report.json"
    input_path.write_text(json.dumps(model_result()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_result_to_report.py",
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
    assert payload["score"] == 4.0


def test_model_result_to_report_cli_rejects_missing_metric(tmp_path) -> None:
    input_path = tmp_path / "model_result.json"
    output_path = tmp_path / "model_report.md"
    input_path.write_text(json.dumps(model_result()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/model_result_to_report.py",
            "--in",
            str(input_path),
            "--out",
            str(output_path),
            "--metric",
            "missing",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "metric not found" in result.stderr
