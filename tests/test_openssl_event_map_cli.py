# ruff: noqa: I001

import json
import subprocess
import sys


SAMPLE = "examples/openssl_preflight/openssl_rsa_keygen_event_map_sample.json"


def test_validate_openssl_event_map_cli_accepts_sample() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_openssl_event_map.py", SAMPLE],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "valid OpenSSL event map" in result.stdout


def test_openssl_event_map_to_report_cli_writes_markdown(tmp_path) -> None:
    output_path = tmp_path / "openssl_event_map.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/openssl_event_map_to_report.py",
            "--in",
            SAMPLE,
            "--out",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert "TraceLeak OpenSSL Event Map Report" in markdown
    assert "prime_candidate_filter" in markdown


def test_openssl_event_map_to_report_cli_writes_json(tmp_path) -> None:
    output_path = tmp_path / "openssl_event_map.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/openssl_event_map_to_report.py",
            "--in",
            SAMPLE,
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
    assert payload["report_type"] == "openssl_event_map_report"
    assert payload["status"] == "event_map_ready"
    assert payload["execution_allowed"] is False


def test_validate_openssl_event_map_cli_rejects_missing_file(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_openssl_event_map.py", str(tmp_path / "missing.json")],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "event map not found" in result.stderr
