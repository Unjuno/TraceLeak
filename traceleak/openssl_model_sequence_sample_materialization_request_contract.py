"""OpenSSL model-sequence sample materialization request contract helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_sample_approval_gate import (
    OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT,
    OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
    REQUIRED_SAMPLE_APPROVAL_SCOPE,
    validate_openssl_model_sequence_sample_approval_gate,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
)

OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_REQUEST_CONTRACT_FORMAT = (
    "traceleak.openssl_model_sequence_sample_materialization_request_contract.v1"
)
SAMPLE_MATERIALIZATION_REQUEST_TRUE_FLAGS = [
    "request_only",
    "metadata_only",
    "payload_free",
    "sample_materialization_allowed",
]
SAMPLE_MATERIALIZATION_REQUEST_FALSE_FLAGS = [
    "sample_ready",
    "model_use_enabled",
    "model_training_allowed",
    "runtime_action_enabled",
    "payload_access_enabled",
]


class OpenSSLModelSequenceSampleMaterializationRequestContractError(ValueError):
    """Raised when a sample materialization request contract is invalid."""


def build_openssl_model_sequence_sample_materialization_request_contract(
    *,
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    planned_sample_path: str,
) -> dict[str, Any]:
    """Build a request-only contract for later sample materialization."""

    validate_openssl_model_sequence_sample_approval_gate(
        gate=approval_gate,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
    )
    contract = {
        "format": OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_REQUEST_CONTRACT_FORMAT,
        "status": "sample_materialization_request_contract_ready",
        "phase": "P19",
        "target": "openssl_model_sequence_sample_materialization_request",
        "mode": "request_contract_only",
        "approval_scope": REQUIRED_SAMPLE_APPROVAL_SCOPE,
        "sample_manifest_format": OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
        "approval_record_format": OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
        "approval_gate_format": OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT,
        "input_digest": sample_manifest["input_digest"],
        "sample_digest": sample_manifest["sample_digest"],
        "source_pin_digest": sample_manifest["source_pin_digest"],
        "trace_contract_digest": sample_manifest["trace_contract_digest"],
        "feature_namespace": sample_manifest["feature_namespace"],
        "sample_id": sample_manifest["sample_id"],
        "planned_sample_path": planned_sample_path,
        "request_only": True,
        "metadata_only": True,
        "payload_free": True,
        "sample_materialization_allowed": True,
        "sample_ready": False,
        "model_use_enabled": False,
        "model_training_allowed": False,
        "runtime_action_enabled": False,
        "payload_access_enabled": False,
    }
    validate_openssl_model_sequence_sample_materialization_request_contract(
        request_contract=contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
    )
    return contract


def validate_openssl_model_sequence_sample_materialization_request_contract(
    *,
    request_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
) -> None:
    """Validate a request-only sample materialization contract."""

    validate_openssl_model_sequence_sample_approval_gate(
        gate=approval_gate,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
    )
    _require_equal(
        request_contract.get("format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_REQUEST_CONTRACT_FORMAT,
        "format",
    )
    _require_equal(
        request_contract.get("status"),
        "sample_materialization_request_contract_ready",
        "status",
    )
    _require_equal(request_contract.get("phase"), "P19", "phase")
    _require_equal(
        request_contract.get("target"),
        "openssl_model_sequence_sample_materialization_request",
        "target",
    )
    _require_equal(request_contract.get("mode"), "request_contract_only", "mode")
    _require_equal(
        request_contract.get("approval_scope"),
        REQUIRED_SAMPLE_APPROVAL_SCOPE,
        "approval_scope",
    )
    _require_equal(
        request_contract.get("sample_manifest_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
        "sample_manifest_format",
    )
    _require_equal(
        request_contract.get("approval_record_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
        "approval_record_format",
    )
    _require_equal(
        request_contract.get("approval_gate_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT,
        "approval_gate_format",
    )
    _require_manifest_binding(request_contract, sample_manifest)
    _require_non_empty_string(
        request_contract.get("planned_sample_path"),
        "planned_sample_path",
    )
    _require_flags(request_contract)


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


def _require_flags(candidate: dict[str, Any]) -> None:
    for flag in SAMPLE_MATERIALIZATION_REQUEST_TRUE_FLAGS:
        _require_equal(candidate.get(flag), True, flag)
    for flag in SAMPLE_MATERIALIZATION_REQUEST_FALSE_FLAGS:
        _require_equal(candidate.get(flag), False, flag)


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceSampleMaterializationRequestContractError(
            f"{name} must be a non-empty string"
        )
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceSampleMaterializationRequestContractError(
            f"{name} must be {expected!r}"
        )
