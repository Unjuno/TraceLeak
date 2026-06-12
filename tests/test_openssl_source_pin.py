# ruff: noqa: I001

import copy
import json
from pathlib import Path

import pytest

from traceleak.openssl_source_pin import (
    OpenSSLSourcePinError,
    load_openssl_source_pin,
    openssl_source_pin_report_dict,
    openssl_source_pin_report_markdown,
    validate_openssl_source_pin,
)


SAMPLE_PATH = Path("examples/openssl_preflight/openssl_source_pin_sample.json")


def sample_manifest() -> dict:
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


def test_openssl_source_pin_sample_validates() -> None:
    manifest = load_openssl_source_pin(SAMPLE_PATH)

    assert manifest["format"] == "traceleak.openssl_source_pin.v1"
    assert manifest["mode"] == "template"
    assert manifest["execution_allowed"] is False
    assert manifest["source"]["exact_commit_sha"] is None


def test_openssl_source_pin_report() -> None:
    report = openssl_source_pin_report_dict(sample_manifest())
    markdown = openssl_source_pin_report_markdown(report)

    assert report["report_type"] == "openssl_source_pin_report"
    assert report["status"] == "source_layout_template_ready"
    assert "crypto/rsa/rsa_gen.c" in report["target_paths"]
    assert "rsa_keygen_entry" in report["event_groups"]
    assert "TraceLeak OpenSSL Source Pin Report" in markdown


def test_openssl_source_pin_rejects_execution_allowed() -> None:
    manifest = sample_manifest()
    manifest["execution_allowed"] = True

    with pytest.raises(OpenSSLSourcePinError, match="execution_allowed"):
        validate_openssl_source_pin(manifest)


def test_openssl_source_pin_pinned_mode_requires_commit() -> None:
    manifest = sample_manifest()
    manifest["mode"] = "pinned"

    with pytest.raises(OpenSSLSourcePinError, match="exact_commit_sha"):
        validate_openssl_source_pin(manifest)


def test_openssl_source_pin_pinned_mode_accepts_commit() -> None:
    manifest = sample_manifest()
    manifest["mode"] = "pinned"
    manifest["source"] = copy.deepcopy(manifest["source"])
    manifest["source"]["exact_commit_sha"] = "1234567890abcdef1234567890abcdef12345678"

    validate_openssl_source_pin(manifest)


def test_openssl_source_pin_rejects_duplicate_target_path() -> None:
    manifest = sample_manifest()
    manifest["source_layout"] = copy.deepcopy(manifest["source_layout"])
    manifest["source_layout"][1]["target_path"] = manifest["source_layout"][0]["target_path"]

    with pytest.raises(OpenSSLSourcePinError, match="duplicate source_layout target_path"):
        validate_openssl_source_pin(manifest)


def test_openssl_source_pin_rejects_invalid_symbol() -> None:
    manifest = sample_manifest()
    manifest["source_layout"] = copy.deepcopy(manifest["source_layout"])
    manifest["source_layout"][0]["required_symbols"].append("not-a-symbol")

    with pytest.raises(OpenSSLSourcePinError, match="invalid symbol"):
        validate_openssl_source_pin(manifest)
