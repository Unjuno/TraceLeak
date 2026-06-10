import json
import subprocess
import sys


def valid_config() -> dict:
    return {
        "experiment_id": "exp_000_synthetic_leak",
        "experiment_type": "synthetic",
        "target": "synthetic-example",
        "view": "redacted",
        "metric": "DeltaH",
        "inputs": {"trace": "examples/synthetic/synthetic_trace_sample.jsonl"},
    }


def test_validate_config_cli_accepts_valid_config(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(valid_config()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_config.py", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_validate_config_cli_json_summary(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(valid_config()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_config.py", "--json", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload[0]["experiment_id"] == "exp_000_synthetic_leak"


def test_validate_config_cli_rejects_raw_public_config(tmp_path) -> None:
    config = valid_config()
    config["view"] = "raw"
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_config.py", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "not allowed" in result.stdout
