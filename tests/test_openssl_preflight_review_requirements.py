import json
from pathlib import Path

import pytest

from traceleak.openssl_preflight import OpenSSLPreflightError, validate_openssl_preflight


SAMPLE_PATH = Path("examples/openssl_preflight/openssl_rsa_keygen_preflight_sample.json")


def sample_manifest() -> dict:
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


def test_openssl_preflight_rejects_missing_event_slot_review_stage() -> None:
    manifest = sample_manifest()
    manifest["pipeline_stages"] = [
        stage for stage in manifest["pipeline_stages"] if stage["name"] != "review_event_slots"
    ]

    with pytest.raises(OpenSSLPreflightError, match="pipeline_stages missing"):
        validate_openssl_preflight(manifest)


def test_openssl_preflight_rejects_missing_human_review_checklist_artifact() -> None:
    manifest = sample_manifest()
    manifest["planned_artifacts"] = [
        artifact
        for artifact in manifest["planned_artifacts"]
        if artifact != "reports/local/openssl_human_review_checklist.md"
    ]

    with pytest.raises(OpenSSLPreflightError, match="planned_artifacts missing"):
        validate_openssl_preflight(manifest)


def test_openssl_preflight_rejects_missing_pending_review_gate() -> None:
    manifest = sample_manifest()
    manifest["gates"] = [
        gate for gate in manifest["gates"] if gate != "pending_review_template_planned"
    ]

    with pytest.raises(OpenSSLPreflightError, match="gates missing"):
        validate_openssl_preflight(manifest)
