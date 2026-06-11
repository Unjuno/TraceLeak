import json
import subprocess
import sys


def l5_claim() -> dict:
    return {
        "claim_id": "synthetic_claim_l5_0001",
        "level": "L5",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "evidence": {
            "patch_verification": {
                "verification_id": "synthetic_patch_0001",
                "status": "reduced",
            },
            "stability": {
                "stability_id": "synthetic_stability_0001",
                "status": "reduced",
            },
        },
        "safety": {
            "public_safe": True,
            "contains_raw_trace": False,
            "contains_secret_equivalent": False,
        },
    }


def test_validate_claim_cli_accepts_valid_claim(tmp_path) -> None:
    path = tmp_path / "claim.json"
    path.write_text(json.dumps(l5_claim()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_claim.py", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout
    assert "L5" in result.stdout


def test_validate_claim_cli_json_summary(tmp_path) -> None:
    path = tmp_path / "claim.json"
    path.write_text(json.dumps(l5_claim()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_claim.py", "--json", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload[0]["claim_id"] == "synthetic_claim_l5_0001"
    assert payload[0]["level"] == "L5"


def test_validate_claim_cli_rejects_invalid_claim(tmp_path) -> None:
    path = tmp_path / "claim.json"
    claim = l5_claim()
    claim["evidence"]["stability"]["status"] = "inconclusive"
    path.write_text(json.dumps(claim), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_claim.py", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "invalid" in result.stdout
    assert "L5 requires" in result.stdout
