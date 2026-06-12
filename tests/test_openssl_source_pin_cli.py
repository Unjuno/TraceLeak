# ruff: noqa: I001

import json
import subprocess
import sys


SAMPLE = "examples/openssl_preflight/openssl_source_pin_sample.json"


def test_validate_openssl_source_pin_cli_accepts_sample() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_openssl_source_pin.py", SAMPLE],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "valid OpenSSL source pin manifest" in result.stdout


def test_openssl_layout_to_report_cli_writes_markdown(tmp_path) -> None:
    output_path = tmp_path / "openssl_layout.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/openssl_layout_to_report.py",
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
    assert "TraceLeak OpenSSL Source Pin Report" in markdown
    assert "crypto/rsa/rsa_gen.c" in markdown


def test_openssl_layout_to_report_cli_writes_json(tmp_path) -> None:
    output_path = tmp_path / "openssl_layout.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/openssl_layout_to_report.py",
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
    assert payload["report_type"] == "openssl_source_pin_report"
    assert payload["status"] == "source_layout_template_ready"
    assert payload["execution_allowed"] is False


def test_validate_openssl_source_pin_cli_rejects_missing_file(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_openssl_source_pin.py", str(tmp_path / "missing.json")],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "source pin manifest not found" in result.stderr
