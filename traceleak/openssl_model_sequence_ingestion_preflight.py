"""OpenSSL model-sequence ingestion preflight helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_handoff_contract import (
    validate_openssl_model_sequence_handoff_contract,
)

OPENSSL_MODEL_SEQUENCE_INGESTION_PREFLIGHT_FORMAT = (
    "traceleak.openssl_model_sequence_ingestion_preflight.v1"
)
REQUIRED_INGESTION_PREFLIGHT_CHECKS = [
    "handoff_contract_valid",
    "artifact_digests_bound",
    "feature_namespace_bound",
    "sample_id_bound",
    "redacted_metadata_only",
    "no_source_text",
    "no_diff",
    "no_commands",
    "no_raw_capture",
    "ingestion_not_allowed",
    "training_not_allowed",
]


class OpenSSLModelSequenceIngestionPreflightError(ValueError):
    """Raised when an OpenSSL model-sequence ingestion preflight is invalid."""


def build_openssl_model_sequence_ingestion_preflight(
    *,
    handoff_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build a preflight report for model-sequence ingestion readiness."""

    validate_openssl_model_sequence_handoff_contract(handoff_contract)
    schema = handoff_contract["handoff_schema"]
    checks = {
        "handoff_contract_valid": True,
        "artifact_digests_bound": bool(handoff_contract["artifact_digests"]),
        "feature_namespace_bound": bool(handoff_contract["feature_namespace"]),
        "sample_id_bound": bool(handoff_contract["sample_id"]),
        "redacted_metadata_only": schema["redacted_metadata_only"],
        "no_source_text": not schema["source_text_embedded"],
        "no_diff": not schema["diff_embedded"],
        "no_commands": not schema["commands_embedded"],
        "no_raw_capture": not schema["raw_capture_embedded"],
        "ingestion_not_allowed": not handoff_contract["model_sequence_ingestion_allowed"],
        "training_not_allowed": not handoff_contract["model_training_allowed"],
    }
    preflight = {
        "format": OPENSSL_MODEL_SEQUENCE_INGESTION_PREFLIGHT_FORMAT,
        "status": "preflight_ready",
        "phase": "P13",
        "target": "openssl_model_sequence_ingestion",
        "mode": "preflight_only",
        "handoff_format": handoff_contract["format"],
        "manifest_format": handoff_contract["manifest_format"],
        "contract_format": handoff_contract["contract_format"],
        "source_pin_digest": handoff_contract["source_pin_digest"],
        "trace_contract_digest": handoff_contract["trace_contract_digest"],
        "artifact_digests": dict(handoff_contract["artifact_digests"]),
        "feature_namespace": handoff_contract["feature_namespace"],
        "sample_id": handoff_contract["sample_id"],
        "checks": checks,
        "blockers": [
            check for check in REQUIRED_INGESTION_PREFLIGHT_CHECKS if not checks.get(check, False)
        ],
        "model_sequence_ingestion_allowed": False,
        "model_training_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_model_sequence_ingestion_preflight(preflight)
    return preflight


def validate_openssl_model_sequence_ingestion_preflight(preflight: dict[str, Any]) -> None:
    """Validate an OpenSSL model-sequence ingestion preflight report."""

    _require_equal(preflight.get("format"), OPENSSL_MODEL_SEQUENCE_INGESTION_PREFLIGHT_FORMAT, "format")
    _require_equal(preflight.get("status"), "preflight_ready", "status")
    _require_equal(preflight.get("phase"), "P13", "phase")
    _require_equal(preflight.get("target"), "openssl_model_sequence_ingestion", "target")
    _require_equal(preflight.get("mode"), "preflight_only", "mode")
    _require_non_empty_string(preflight.get("handoff_format"), "handoff_format")
    _require_non_empty_string(preflight.get("manifest_format"), "manifest_format")
    _require_non_empty_string(preflight.get("contract_format"), "contract_format")
    _require_non_empty_string(preflight.get("source_pin_digest"), "source_pin_digest")
    _require_non_empty_string(preflight.get("trace_contract_digest"), "trace_contract_digest")
    artifact_digests = _require_dict(preflight.get("artifact_digests"), "artifact_digests")
    if not artifact_digests:
        raise OpenSSLModelSequenceIngestionPreflightError("artifact_digests must be non-empty")
    for name, digest in artifact_digests.items():
        _require_non_empty_string(name, "artifact_digests key")
        _require_non_empty_string(digest, f"artifact_digests.{name}")
    _require_non_empty_string(preflight.get("feature_namespace"), "feature_namespace")
    _require_non_empty_string(preflight.get("sample_id"), "sample_id")
    checks = _require_dict(preflight.get("checks"), "checks")
    for check in REQUIRED_INGESTION_PREFLIGHT_CHECKS:
        if check not in checks:
            raise OpenSSLModelSequenceIngestionPreflightError(f"checks missing: {check}")
        if not isinstance(checks[check], bool):
            raise OpenSSLModelSequenceIngestionPreflightError(f"checks.{check} must be a bool")
    blockers = preflight.get("blockers")
    if not isinstance(blockers, list):
        raise OpenSSLModelSequenceIngestionPreflightError("blockers must be a list")
    expected_blockers = [
        check for check in REQUIRED_INGESTION_PREFLIGHT_CHECKS if not checks.get(check, False)
    ]
    _require_equal(blockers, expected_blockers, "blockers")
    _require_equal(
        preflight.get("model_sequence_ingestion_allowed"),
        False,
        "model_sequence_ingestion_allowed",
    )
    _require_equal(preflight.get("model_training_allowed"), False, "model_training_allowed")
    _require_equal(preflight.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(preflight.get("compile_allowed"), False, "compile_allowed")
    _require_equal(preflight.get("execution_allowed"), False, "execution_allowed")
    _require_equal(preflight.get("raw_capture_allowed"), False, "raw_capture_allowed")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceIngestionPreflightError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceIngestionPreflightError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceIngestionPreflightError(f"{name} must be {expected!r}")
