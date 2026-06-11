import json
import subprocess
import sys


def patch_result() -> dict:
    return {
        "verification_id": "synthetic_patch_0001",
        "target": "synthetic-leak",
        "view": "redacted",
        "metric": "DeltaH",
        "before": {"run_id": "before", "score": 4.0, "report": "before.md"},
        "after": {"run_id": "after", "score": 1.0, "report": "after.md"},
        "delta": 3.0,
        "status": "reduced",
        "changed_groups": [
            {
                "group_id": "synthetic_branch_event",
                "location": "examples/synthetic/target.py:19",
                "before_contribution": 3.0,
                "after_contribution": 0.5,
            }
        ],
    }


def test_patch_verification_to_report_cli_writes_markdown(tmp_path) -> None:
    input_path = tmp_path / "patch_verification.json"
    output_path = tmp_path / "patch_report.md"
    input_path.write_text(json.dumps(patch_result()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/patch_verification_to_report.py",
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


def test_patch_verification_to_report_cli_writes_json(tmp_path) -> None:
    input_path = tmp_path / "patch_verification.json"
    output_path = tmp_path / "patch_report.json"
    input_path.write_text(json.dumps(patch_result()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/patch_verification_to_report.py",
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
    assert payload["report_type"] == "patch_verification"
    assert payload["status"] == "reduced"


def test_patch_verification_to_report_cli_rejects_invalid_input(tmp_path) -> None:
    input_path = tmp_path / "patch_verification.json"
    output_path = tmp_path / "patch_report.md"
    data = patch_result()
    data["delta"] = 99.0
    input_path.write_text(json.dumps(data), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/patch_verification_to_report.py",
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
