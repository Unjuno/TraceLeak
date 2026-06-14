"""OpenSSL model-sequence sample approval gate helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_sample_manifest import (
    OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
)

OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT = (
    "traceleak.openssl_model_sequence_sample_approval_gate.v1"
)
OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT = (
    "traceleak.openssl_model_sequence_sample_approval_record.v1"
)
REQUIRED_SAMPLE_APPROVAL_SCOPE = "sample_materialization_request_only"
SAMPLE_APPROVAL_FALSE_FLAGS = [
    "sample_ready",
    "model_use_enabled",
    "model_training_allowed",
    "runtime_action_enabled",
    "payload_access_enabled",
]
SAMPLE_APPROVAL_TRUE_FLAGS = [
    "metadata_only",
    "payload_free",
]


class OpenSSLModelSequenceSampleApprovalGateError(ValueError):
    """Raised when an OpenSSL model-sequence sample approval gate is invalid."""


def build_openssl_model_sequence_sample_approval_record(
    *,
    sample_manifest: dict[str, Any],
    reviewer: str,
    reviewed_at: str,
) -> dict[str, Any]:
    """Build a human review record for sample materialization request approval."""

    _validate_sample_manifest_header(sample_manifest)
    record = {
        "format": OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
        "status": "sample_review_approved",
        "decision": "approved",
        "approval_scope": REQUIRED_SAMPLE_APPROVAL_SCOPE,
        "sample_manifest_format": sample_manifest["format"],
        "input_digest": sample_manifest["input_digest"],
        "sample_digest": sample_manifest["sample_digest"],
        "source_pin_digest": sample_manifest["source_pin_digest"],
        "trace_contract_digest": sample_manifest["trace_contract_digest"],
        "feature_namespace": sample_manifest["feature_namespace"],
        "sample_id": sample_manifest["sample_id"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "human_review_completed": True,
        "sample_materialization_request_approved": True,
        "sample_materialization_allowed": True,
        "metadata_only": True,
        "payload_free": True,
        "sample_ready": False,
        "model_use_enabled": False,
        "model_training_allowed": False,
        "runtime_action_enabled": False,
        "payload_access_enabled": False,
    }
    validate_openssl_model_sequence_sample_approval_record(
        approval_record=record,
        sample_manifest=sample_manifest,
    )
    return record


def build_openssl_model_sequence_sample_approval_gate(
    *,
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
) -> dict[str, Any]:
    """Build a satisfied approval gate for sample materialization request approval."""

    _validate_sample_manifest_header(sample_manifest)
    validate_openssl_model_sequence_sample_approval_record(
        approval_record=approval_record,
        sample_manifest=sample_manifest,
    )
    gate = {
        "format": OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT,
        "status": "sample_approval_gate_satisfied",
        "phase": "P18",
        "target": "openssl_model_sequence_sample_approval",
        "mode": "approval_gate_only",
        "approval_scope": REQUIRED_SAMPLE_APPROVAL_SCOPE,
        "sample_manifest_format": sample_manifest["format"],
        "approval_record_format": approval_record["format"],
        "input_digest": sample_manifest["input_digest"],
        "sample_digest": sample_manifest["sample_digest"],
        "source_pin_digest": sample_manifest["source_pin_digest"],
        "trace_contract_digest": sample_manifest["trace_contract_digest"],
        "feature_namespace": sample_manifest["feature_namespace"],
        "sample_id": sample_manifest["sample_id"],
        "approval_record_accepted": True,
        "sample_materialization_request_approved": True,
        "sample_materialization_allowed": True,
        "metadata_only": True,
        "payload_free": True,
        "sample_ready": False,
        "model_use_enabled": False,
        "model_training_allowed": False,
        "runtime_action_enabled": False,
        "payload_access_enabled": False,
    }
    validate_openssl_model_sequence_sample_approval_gate(
        gate=gate,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
    )
    return gate


def validate_openssl_model_sequence_sample_approval_record(
    *,
    approval_record: dict[str, Any],
    sample_manifest: dict[str, Any],
) -> None:
    """Validate a sample approval record against a metadata-only sample manifest."""

    _validate_sample_manifest_header(sample_manifest)
    _require_equal(
        approval_record.get("format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
        "format",
    )
    _require_equal(approval_record.get("status"), "sample_review_approved", "status")
    _require_equal(approval_record.get("decision"), "approved", "decision")
    _require_equal(
        approval_record.get("approval_scope"),
        REQUIRED_SAMPLE_APPROVAL_SCOPE,
        "approval_scope",
    )
    _require_equal(
        approval_record.get("sample_manifest_format"),
        sample_manifest["format"],
        "sample_manifest_format",
    )
    _require_manifest_binding(approval_record, sample_manifest)
    _require_non_empty_string(approval_record.get("reviewer"), "reviewer")
    _require_non_empty_string(approval_record.get("reviewed_at"), "reviewed_at")
    _require_equal(
        approval_record.get("human_review_completed"),
        True,
        "human_review_completed",
    )
    _require_equal(
        approval_record.get("sample_materialization_request_approved"),
        True,
        "sample_materialization_request_approved",
    )
    _require_equal(
        approval_record.get("sample_materialization_allowed"),
        True,
        "sample_materialization_allowed",
    )
    _require_gate_flags(approval_record)


def validate_openssl_model_sequence_sample_approval_gate(
    *,
    gate: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
) -> None:
    """Validate a satisfied sample approval gate."""

    _validate_sample_manifest_header(sample_manifest)
    validate_openssl_model_sequence_sample_approval_record(
        approval_record=approval_record,
        sample_manifest=sample_manifest,
    )
    _require_equal(
        gate.get("format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT,
        "format",
    )
    _require_equal(gate.get("status"), "sample_approval_gate_satisfied", "status")
    _require_equal(gate.get("phase"), "P18", "phase")
    _require_equal(
        gate.get("target"),
        "openssl_model_sequence_sample_approval",
        "target",
    )
    _require_equal(gate.get("mode"), "approval_gate_only", "mode")
    _require_equal(
        gate.get("approval_scope"),
        REQUIRED_SAMPLE_APPROVAL_SCOPE,
        "approval_scope",
    )
    _require_equal(
        gate.get("sample_manifest_format"),
        sample_manifest["format"],
        "sample_manifest_format",
    )
    _require_equal(
        gate.get("approval_record_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
        "approval_record_format",
    )
    _require_manifest_binding(gate, sample_manifest)
    _require_equal(
        gate.get("approval_record_accepted"),
        True,
        "approval_record_accepted",
    )
    _require_equal(
        gate.get("sample_materialization_request_approved"),
        True,
        "sample_materialization_request_approved",
    )
    _require_equal(
        gate.get("sample_materialization_allowed"),
        True,
        "sample_materialization_allowed",
    )
    _require_gate_flags(gate)


def _validate_sample_manifest_header(sample_manifest: dict[str, Any]) -> None:
    _require_equal(
        sample_manifest.get("format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
        "sample_manifest.format",
    )
    _require_equal(
        sample_manifest.get("status"),
        "sample_manifest_ready",
        "sample_manifest.status",
    )
    _require_equal(sample_manifest.get("phase"), "P17", "sample_manifest.phase")
    _require_equal(
        sample_manifest.get("target"),
        "openssl_model_sequence_sample_manifest",
        "sample_manifest.target",
    )
    _require_equal(sample_manifest.get("mode"), "metadata_only", "sample_manifest.mode")
    _require_non_empty_string(
        sample_manifest.get("input_digest"),
        "sample_manifest.input_digest",
    )
    _require_non_empty_string(
        sample_manifest.get("sample_digest"),
        "sample_manifest.sample_digest",
    )
    _require_non_empty_string(
        sample_manifest.get("source_pin_digest"),
        "sample_manifest.source_pin_digest",
    )
    _require_non_empty_string(
        sample_manifest.get("trace_contract_digest"),
        "sample_manifest.trace_contract_digest",
    )
    _require_non_empty_string(
        sample_manifest.get("feature_namespace"),
        "sample_manifest.feature_namespace",
    )
    _require_non_empty_string(
        sample_manifest.get("sample_id"),
        "sample_manifest.sample_id",
    )
    manifest_schema = _require_dict(
        sample_manifest.get("manifest_schema"),
        "manifest_schema",
    )
    _require_equal(
        manifest_schema.get("metadata_only"),
        True,
        "manifest_schema.metadata_only",
    )
    _require_equal(
        manifest_schema.get("payload_free"),
        True,
        "manifest_schema.payload_free",
    )
    _require_equal(
        sample_manifest.get("sample_ready"),
        False,
        "sample_manifest.sample_ready",
    )
    _require_equal(
        sample_manifest.get("model_use_enabled"),
        False,
        "sample_manifest.model_use_enabled",
    )


def _require_manifest_binding(
    candidate: dict[str, Any],
    sample_manifest: dict[str, Any],
) -> None:
    for field in [
        "input_digest",
        "sample_digest",
        "source_pin_digest",
        "trace_contract_digest",
        "feature_namespace",
        "sample_id",
    ]:
        _require_equal(candidate.get(field), sample_manifest[field], field)


def _require_gate_flags(candidate: dict[str, Any]) -> None:
    for flag in SAMPLE_APPROVAL_TRUE_FLAGS:
        _require_equal(candidate.get(flag), True, flag)
    for flag in SAMPLE_APPROVAL_FALSE_FLAGS:
        _require_equal(candidate.get(flag), False, flag)


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceSampleApprovalGateError(
            f"{name} must be an object"
        )
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceSampleApprovalGateError(
            f"{name} must be a non-empty string"
        )
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceSampleApprovalGateError(
            f"{name} must be {expected!r}"
        )
