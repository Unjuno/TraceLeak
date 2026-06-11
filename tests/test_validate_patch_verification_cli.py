import json
import subprocess
import sys


def valid_result() -> dict:
    return {
        "verification_id": "synthetic_patch_0001",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "before": {"run_id": "before", "score": 4.0},
        "after": {"run_id": "after", "score": 1.0},
        "delta": 3.0,
        "status": "reduced",
    }


def test_validate_patch_verification_cli_accepts_valid_result(tmp_path) -> None:
    path = tmp_path / "patch_verification.json"
    path.write_text(json.dumps(valid_result()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_patch_verification.py", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_validate_patch_verification_cli_json_summary(tmp_path) -> None:
    path = tmp_path / "patch_verification.json"
    path.write_text(json.dumps(valid_result()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_patch_verification.py", "--json", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload[0]["verification_id"] == "synthetic_patch_0001"
    assert payload[0]["status"] == "reduced"


def test_validate_patch_verification_cli_rejects_missing_input(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_patch_verification.py", str(tmp_path / "missing.json")],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "patch verification file not found" in result.stdout
