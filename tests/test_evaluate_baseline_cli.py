import json
import subprocess
import sys


def sample_input() -> dict:
    return {
        "target": "synthetic-example",
        "view": "redacted",
        "label_name": "synthetic_bucket",
        "examples": [
            {"run_id": "r1", "label": "A", "features": {"phase=alpha": 1.0}},
            {"run_id": "r2", "label": "A", "features": {"phase=alpha": 1.0}},
            {"run_id": "r3", "label": "B", "features": {"phase=beta": 1.0}},
            {"run_id": "r4", "label": "B", "features": {"phase=beta": 1.0}},
        ],
    }


def test_evaluate_baseline_cli_prints_json(tmp_path) -> None:
    input_path = tmp_path / "baseline.json"
    input_path.write_text(json.dumps(sample_input()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/evaluate_baseline.py", "--in", str(input_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["example_count"] == 4
    assert payload["label_distribution"] == {"A": 2, "B": 2}


def test_evaluate_baseline_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "baseline.json"
    output_path = tmp_path / "baseline_result.json"
    input_path.write_text(json.dumps(sample_input()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_baseline.py",
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
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["target"] == "synthetic-example"


def test_evaluate_baseline_cli_reports_missing_input(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_baseline.py",
            "--in",
            str(tmp_path / "missing.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "input file not found" in result.stderr
