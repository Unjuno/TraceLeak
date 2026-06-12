# ruff: noqa: I001

import copy
import json
from pathlib import Path

import pytest

from traceleak.openssl_preflight import (
    OpenSSLPreflightError,
    load_openssl_preflight,
    openssl_preflight_report_dict,
    openssl_preflight_report_markdown,
    validate_openssl_preflight,
)


SAMPLE_PATH = Path("examples/openssl_preflight/openssl_rsa_keygen_preflight_sample.json")


def sample_manifest() -> dict:
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


def test_openssl_preflight_sample_validates() -> None:
    manifest = load_openssl_preflight(SAMPLE_PATH)

    assert manifest["format"] == "traceleak.openssl_preflight.v1"
    assert manifest["mode"] == "preflight_only"
    assert manifest["execution_allowed"] is False


def test_openssl_preflight_report() -> None:
    report = openssl_preflight_report_dict(sample_manifest())
    markdown = openssl_preflight_report_markdown(report)

    assert report["report_type"] == "openssl_preflight_report"
    assert report["status"] == "preflight_ready"
    assert report["execution_allowed"] is False
    assert report["raw_secret_capture_allowed"] is False
    assert "TraceLeak OpenSSL Preflight Report" in markdown
    assert "no_raw_secret_fields" in markdown


def test_openssl_preflight_report_includes_review_only_chain() -> None:
    report = openssl_preflight_report_dict(sample_manifest())
    markdown = openssl_preflight_report_markdown(report)

    assert "review_event_slots" in markdown
    assert "build_human_review_checklist" in markdown
    assert "build_pending_review" in markdown
    assert "event_slot_review_planned" in markdown
    assert "human_review_checklist_planned" in markdown
    assert "pending_review_template_planned" in markdown


def test_openssl_preflight_rejects_execution_allowed() -> None:
    manifest = sample_manifest()
    manifest["execution_allowed"] = True

    with pytest.raises(OpenSSLPreflightError, match="execution_allowed"):
        validate_openssl_preflight(manifest)


def test_openssl_preflight_rejects_raw_secret_capture() -> None:
    manifest = sample_manifest()
    manifest["instrumentation"] = copy.deepcopy(manifest["instrumentation"])
    manifest["instrumentation"]["raw_secret_capture_allowed"] = True

    with pytest.raises(OpenSSLPreflightError, match="raw_secret_capture_allowed"):
        validate_openssl_preflight(manifest)


def test_openssl_preflight_rejects_missing_required_secret_blocker() -> None:
    manifest = sample_manifest()
    manifest["instrumentation"] = copy.deepcopy(manifest["instrumentation"])
    manifest["instrumentation"]["disallowed_fields"] = [
        item for item in manifest["instrumentation"]["disallowed_fields"] if item != "private_key"
    ]

    with pytest.raises(OpenSSLPreflightError, match="disallowed_fields missing"):
        validate_openssl_preflight(manifest)


def test_openssl_preflight_rejects_missing_required_control() -> None:
    manifest = sample_manifest()
    manifest["required_controls"] = ["public_only_baseline"]

    with pytest.raises(OpenSSLPreflightError, match="required_controls missing"):
        validate_openssl_preflight(manifest)
