import json
import subprocess
import sys


def valid_input() -> dict:
    return {
        "stability_id": "synthetic_stability_0001",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "before_scores": [4.2, 4.0, 4.1, 3.9, 4.05],
        "after_scores": [1.1, 1.0, 1.2, 0.95, 1.05],
    }


def test_evaluate_stability_cli_prints_json(tmp_path) -> None:
    input_path = tmp_path / "stability.json"
    input_path.write_text(json.dumps(valid_input()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/evaluate_stability.py", str(input_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result_type"] == "repeated_run_stability"
    assert payload["summary"]["status"] == "reduced"


def test_evaluate_stability_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "stability.json"
    output_path = tmp_path / "stability_result.json"
    input_path.write_text(json.dumps(valid_input()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_stability.py",
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
    assert payload["stability_id"] == "synthetic_stability_0001"


def test_evaluate_stability_cli_rejects_missing_input(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/evaluate_stability.py", str(tmp_path / "missing.json")],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "stability input file not found" in result.stderr
