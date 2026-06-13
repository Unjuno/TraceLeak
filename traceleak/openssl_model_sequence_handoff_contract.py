"""OpenSSL materialization manifest to model-sequence handoff helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_materialization_output_manifest import (
    validate_openssl_materialization_output_manifest,
)

OPENSSL_MODEL_SEQUENCE_HANDOFF_CONTRACT_FORMAT = (
    "traceleak.openssl_model_sequence_handoff_contract.v1"
)
HANDOFF_SCHEMA_FLAGS = [
    "manifest_digest_bound",
    "source_pin_digest_bound",
    "trace_contract_digest_bound",
    "redacted_metadata_only",
    "source_text_embedded",
    "diff_embedded",
    "commands_embedded",
    "raw_capture_embedded",
]


class OpenSSLModelSequenceHandoffContractError(ValueError):
    """Raised when an OpenSSL model-sequence handoff contract is invalid."""


def build_openssl_model_sequence_handoff_contract(
    *,
    materialization_manifest: dict[str, Any],
    output_contract: dict[str, Any],
    feature_namespace: str,
    sample_id: str,
) -> dict[str, Any]:
    """Build a metadata-only handoff contract for model-sequence ingestion."""

    validate_openssl_materialization_output_manifest(
        manifest=materialization_manifest,
        output_contract=output_contract,
    )
    handoff = {
        "format": OPENSSL_MODEL_SEQUENCE_HANDOFF_CONTRACT_FORMAT,
        "status": "handoff_contract_ready",
        "phase": "P12",
        "target": "openssl_manifest_to_model_sequence",
        "mode": "contract_only",
        "manifest_format": materialization_manifest["format"],
        "contract_format": output_contract["format"],
        "source_pin_digest": materialization_manifest["source_pin_digest"],
        "trace_contract_digest": materialization_manifest["trace_contract_digest"],
        "artifact_digests": dict(materialization_manifest["artifact_digests"]),
        "feature_namespace": feature_namespace,
        "sample_id": sample_id,
        "handoff_schema": {
            "manifest_digest_bound": True,
            "source_pin_digest_bound": True,
            "trace_contract_digest_bound": True,
            "redacted_metadata_only": True,
            "source_text_embedded": False,
            "diff_embedded": False,
            "commands_embedded": False,
            "raw_capture_embedded": False,
        },
        "handoff_generated": False,
        "model_sequence_ingestion_allowed": False,
        "model_training_allowed": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_model_sequence_handoff_contract(handoff)
    return handoff


def validate_openssl_model_sequence_handoff_contract(handoff: dict[str, Any]) -> None:
    """Validate an OpenSSL model-sequence handoff contract."""

    _require_equal(handoff.get("format"), OPENSSL_MODEL_SEQUENCE_HANDOFF_CONTRACT_FORMAT, "format")
    _require_equal(handoff.get("status"), "handoff_contract_ready", "status")
    _require_equal(handoff.get("phase"), "P12", "phase")
    _require_equal(handoff.get("target"), "openssl_manifest_to_model_sequence", "target")
    _require_equal(handoff.get("mode"), "contract_only", "mode")
    _require_non_empty_string(handoff.get("manifest_format"), "manifest_format")
    _require_non_empty_string(handoff.get("contract_format"), "contract_format")
    _require_non_empty_string(handoff.get("source_pin_digest"), "source_pin_digest")
    _require_non_empty_string(handoff.get("trace_contract_digest"), "trace_contract_digest")
    artifact_digests = _require_dict(handoff.get("artifact_digests"), "artifact_digests")
    if not artifact_digests:
        raise OpenSSLModelSequenceHandoffContractError("artifact_digests must be non-empty")
    for name, digest in artifact_digests.items():
        _require_non_empty_string(name, "artifact_digests key")
        _require_non_empty_string(digest, f"artifact_digests.{name}")
    _require_non_empty_string(handoff.get("feature_namespace"), "feature_namespace")
    _require_non_empty_string(handoff.get("sample_id"), "sample_id")
    schema = _require_dict(handoff.get("handoff_schema"), "handoff_schema")
    for flag in HANDOFF_SCHEMA_FLAGS:
        if flag not in schema:
            raise OpenSSLModelSequenceHandoffContractError(f"handoff_schema missing: {flag}")
        if not isinstance(schema[flag], bool):
            raise OpenSSLModelSequenceHandoffContractError(f"handoff_schema.{flag} must be a bool")
    _require_equal(schema["manifest_digest_bound"], True, "handoff_schema.manifest_digest_bound")
    _require_equal(schema["source_pin_digest_bound"], True, "handoff_schema.source_pin_digest_bound")
    _require_equal(schema["trace_contract_digest_bound"], True, "handoff_schema.trace_contract_digest_bound")
    _require_equal(schema["redacted_metadata_only"], True, "handoff_schema.redacted_metadata_only")
    _require_equal(schema["source_text_embedded"], False, "handoff_schema.source_text_embedded")
    _require_equal(schema["diff_embedded"], False, "handoff_schema.diff_embedded")
    _require_equal(schema["commands_embedded"], False, "handoff_schema.commands_embedded")
    _require_equal(schema["raw_capture_embedded"], False, "handoff_schema.raw_capture_embedded")
    _require_equal(handoff.get("handoff_generated"), False, "handoff_generated")
    _require_equal(
        handoff.get("model_sequence_ingestion_allowed"),
        False,
        "model_sequence_ingestion_allowed",
    )
    _require_equal(handoff.get("model_training_allowed"), False, "model_training_allowed")
    _require_equal(handoff.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(handoff.get("compile_allowed"), False, "compile_allowed")
    _require_equal(handoff.get("execution_allowed"), False, "execution_allowed")
    _require_equal(handoff.get("raw_capture_allowed"), False, "raw_capture_allowed")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceHandoffContractError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceHandoffContractError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceHandoffContractError(f"{name} must be {expected!r}")
