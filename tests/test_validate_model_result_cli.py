import json
import subprocess
import sys


def valid_result() -> dict:
    return {
        "experiment_id": "exp_001_synthetic_generated",
        "target": "synthetic-leak",
        "view": "redacted",
        "model": {"name": "placeholder", "type": "neural"},
        "metrics": {"test": {"accuracy": 0.875}},
    }


def test_validate_model_result_cli_accepts_valid_result(tmp_path) -> None:
    path = tmp_path / "model_result.json"
    path.write_text(json.dumps(valid_result()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_model_result.py", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_validate_model_result_cli_json_summary(tmp_path) -> None:
    path = tmp_path / "model_result.json"
    path.write_text(json.dumps(valid_result()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_model_result.py", "--json", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload[0]["experiment_id"] == "exp_001_synthetic_generated"


def test_validate_model_result_cli_rejects_missing_input(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_model_result.py", str(tmp_path / "missing.json")],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "model result file not found" in result.stdout
