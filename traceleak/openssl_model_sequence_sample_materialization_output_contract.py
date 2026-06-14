"""OpenSSL model-sequence sample materialization output contract helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_sample_approval_gate import (
    OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT,
    OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
)
from traceleak.openssl_model_sequence_sample_manifest import (
    OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
)
from traceleak.openssl_model_sequence_sample_materialization_request_contract import (
    OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_REQUEST_CONTRACT_FORMAT,
    REQUIRED_SAMPLE_APPROVAL_SCOPE,
    validate_openssl_model_sequence_sample_materialization_request_contract,
)

OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT = (
    "traceleak.openssl_model_sequence_sample_materialization_output_contract.v1"
)
SAMPLE_MATERIALIZATION_OUTPUT_SCHEMA_TRUE_FLAGS = [
    "request_contract_bound",
    "manifest_required",
    "digest_required",
    "metadata_only",
    "payload_free",
]
SAMPLE_MATERIALIZATION_OUTPUT_SCHEMA_FALSE_FLAGS = [
    "sample_artifact_generated",
    "model_use_enabled",
    "model_training_allowed",
    "runtime_action_enabled",
    "payload_access_enabled",
]


class OpenSSLModelSequenceSampleMaterializationOutputContractError(ValueError):
    """Raised when a sample materialization output contract is invalid."""


def build_openssl_model_sequence_sample_materialization_output_contract(
    *,
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
    output_manifest_path: str,
) -> dict[str, Any]:
    """Build a contract for a future metadata-only sample artifact manifest."""

    validate_openssl_model_sequence_sample_materialization_request_contract(
        request_contract=request_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
    )
    contract = {
        "format": OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT,
        "status": "sample_materialization_output_contract_ready",
        "phase": "P20",
        "target": "openssl_model_sequence_sample_materialization_output",
        "mode": "output_contract_only",
        "approval_scope": REQUIRED_SAMPLE_APPROVAL_SCOPE,
        "sample_manifest_format": OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
        "approval_record_format": OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
        "approval_gate_format": OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT,
        "request_contract_format": (
            OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_REQUEST_CONTRACT_FORMAT
        ),
        "input_digest": sample_manifest["input_digest"],
        "sample_digest": sample_manifest["sample_digest"],
        "source_pin_digest": sample_manifest["source_pin_digest"],
        "trace_contract_digest": sample_manifest["trace_contract_digest"],
        "feature_namespace": sample_manifest["feature_namespace"],
        "sample_id": sample_manifest["sample_id"],
        "planned_sample_path": request_contract["planned_sample_path"],
        "output_manifest_path": output_manifest_path,
        "output_schema": {
            "request_contract_bound": True,
            "manifest_required": True,
            "digest_required": True,
            "metadata_only": True,
            "payload_free": True,
            "sample_artifact_generated": False,
            "model_use_enabled": False,
            "model_training_allowed": False,
            "runtime_action_enabled": False,
            "payload_access_enabled": False,
        },
    }
    validate_openssl_model_sequence_sample_materialization_output_contract(
        output_contract=contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    return contract


def validate_openssl_model_sequence_sample_materialization_output_contract(
    *,
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
) -> None:
    """Validate a metadata-only sample materialization output contract."""

    validate_openssl_model_sequence_sample_materialization_request_contract(
        request_contract=request_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
    )
    _require_equal(
        output_contract.get("format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT,
        "format",
    )
    _require_equal(
        output_contract.get("status"),
        "sample_materialization_output_contract_ready",
        "status",
    )
    _require_equal(output_contract.get("phase"), "P20", "phase")
    _require_equal(
        output_contract.get("target"),
        "openssl_model_sequence_sample_materialization_output",
        "target",
    )
    _require_equal(output_contract.get("mode"), "output_contract_only", "mode")
    _require_equal(
        output_contract.get("approval_scope"),
        REQUIRED_SAMPLE_APPROVAL_SCOPE,
        "approval_scope",
    )
    _require_equal(
        output_contract.get("sample_manifest_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
        "sample_manifest_format",
    )
    _require_equal(
        output_contract.get("approval_record_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_RECORD_FORMAT,
        "approval_record_format",
    )
    _require_equal(
        output_contract.get("approval_gate_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_APPROVAL_GATE_FORMAT,
        "approval_gate_format",
    )
    _require_equal(
        output_contract.get("request_contract_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_REQUEST_CONTRACT_FORMAT,
        "request_contract_format",
    )
    _require_manifest_binding(output_contract, sample_manifest)
    _require_equal(
        output_contract.get("planned_sample_path"),
        request_contract["planned_sample_path"],
        "planned_sample_path",
    )
    _require_non_empty_string(
        output_contract.get("output_manifest_path"),
        "output_manifest_path",
    )
    _require_output_schema(output_contract)


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


def _require_output_schema(candidate: dict[str, Any]) -> None:
    schema = _require_dict(candidate.get("output_schema"), "output_schema")
    for flag in SAMPLE_MATERIALIZATION_OUTPUT_SCHEMA_TRUE_FLAGS:
        if flag not in schema:
            raise OpenSSLModelSequenceSampleMaterializationOutputContractError(
                f"output_schema missing: {flag}"
            )
        _require_equal(schema[flag], True, f"output_schema.{flag}")
    for flag in SAMPLE_MATERIALIZATION_OUTPUT_SCHEMA_FALSE_FLAGS:
        if flag not in schema:
            raise OpenSSLModelSequenceSampleMaterializationOutputContractError(
                f"output_schema missing: {flag}"
            )
        _require_equal(schema[flag], False, f"output_schema.{flag}")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceSampleMaterializationOutputContractError(
            f"{name} must be an object"
        )
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceSampleMaterializationOutputContractError(
            f"{name} must be a non-empty string"
        )
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceSampleMaterializationOutputContractError(
            f"{name} must be {expected!r}"
        )
