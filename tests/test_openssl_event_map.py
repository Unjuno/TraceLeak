# ruff: noqa: I001

import copy
import json
from pathlib import Path

import pytest

from traceleak.openssl_event_map import (
    OpenSSLEventMapError,
    load_openssl_event_map,
    openssl_event_map_report_dict,
    openssl_event_map_report_markdown,
    validate_openssl_event_map,
)


SAMPLE_PATH = Path("examples/openssl_preflight/openssl_rsa_keygen_event_map_sample.json")


def sample_event_map() -> dict:
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


def test_openssl_event_map_sample_validates() -> None:
    event_map = load_openssl_event_map(SAMPLE_PATH)

    assert event_map["format"] == "traceleak.openssl_event_map.v1"
    assert event_map["execution_allowed"] is False
    assert event_map["trace_view"] == "redacted"
    assert len(event_map["event_groups"]) >= 5


def test_openssl_event_map_report() -> None:
    report = openssl_event_map_report_dict(sample_event_map())
    markdown = openssl_event_map_report_markdown(report)

    assert report["report_type"] == "openssl_event_map_report"
    assert report["status"] == "event_map_ready"
    assert report["execution_allowed"] is False
    assert "crypto/rsa/rsa_gen.c" in report["target_paths"]
    assert "TraceLeak OpenSSL Event Map Report" in markdown
    assert "prime_candidate_filter" in markdown


def test_openssl_event_map_rejects_execution_allowed() -> None:
    event_map = sample_event_map()
    event_map["execution_allowed"] = True

    with pytest.raises(OpenSSLEventMapError, match="execution_allowed"):
        validate_openssl_event_map(event_map)


def test_openssl_event_map_rejects_raw_secret_capture() -> None:
    event_map = sample_event_map()
    event_map["raw_secret_capture_allowed"] = True

    with pytest.raises(OpenSSLEventMapError, match="raw_secret_capture_allowed"):
        validate_openssl_event_map(event_map)


def test_openssl_event_map_rejects_duplicate_group_id() -> None:
    event_map = sample_event_map()
    event_map["event_groups"] = copy.deepcopy(event_map["event_groups"])
    event_map["event_groups"][1]["group_id"] = event_map["event_groups"][0]["group_id"]

    with pytest.raises(OpenSSLEventMapError, match="duplicate event group_id"):
        validate_openssl_event_map(event_map)


def test_openssl_event_map_rejects_forbidden_raw_redacted_value() -> None:
    event_map = sample_event_map()
    event_map["event_groups"] = copy.deepcopy(event_map["event_groups"])
    event_map["event_groups"][0]["redacted_values"].append("private_key")

    with pytest.raises(OpenSSLEventMapError, match="forbidden raw names"):
        validate_openssl_event_map(event_map)
