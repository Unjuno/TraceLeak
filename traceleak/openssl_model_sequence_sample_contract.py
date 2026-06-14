"""OpenSSL model-sequence sample contract helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_input_manifest import (
    validate_openssl_model_sequence_input_manifest,
)

OPENSSL_MODEL_SEQUENCE_SAMPLE_CONTRACT_FORMAT = "traceleak.openssl_model_sequence_sample_contract.v1"
SAMPLE_CONTRACT_FLAGS = [
    "manifest_bound",
    "feature_fields_declared",
    "label_fields_declared",
    "metadata_fields_declared",
    "metadata_only",
    "payload_free",
]


class OpenSSLModelSequenceSampleContractError(ValueError):
    """Raised when an OpenSSL model-sequence sample contract is invalid."""


def build_openssl_model_sequence_sample_contract(
    *,
    input_manifest: dict[str, Any],
    input_contract: dict[str, Any],
    feature_fields: list[str],
    label_fields: list[str],
    metadata_fields: list[str],
) -> dict[str, Any]:
    """Build a contract for future model-sequence sample preparation."""

    validate_openssl_model_sequence_input_manifest(
        manifest=input_manifest,
        input_contract=input_contract,
    )
    contract = {
        "format": OPENSSL_MODEL_SEQUENCE_SAMPLE_CONTRACT_FORMAT,
        "status": "sample_contract_ready",
        "phase": "P16",
        "target": "openssl_model_sequence_sample",
        "mode": "contract_only",
        "input_manifest_format": input_manifest["format"],
        "input_contract_format": input_contract["format"],
        "input_digest": input_manifest["input_digest"],
        "source_pin_digest": input_manifest["source_pin_digest"],
        "trace_contract_digest": input_manifest["trace_contract_digest"],
        "feature_namespace": input_manifest["feature_namespace"],
        "sample_id": input_manifest["sample_id"],
        "feature_fields": list(feature_fields),
        "label_fields": list(label_fields),
        "metadata_fields": list(metadata_fields),
        "sample_schema": {
            "manifest_bound": True,
            "feature_fields_declared": True,
            "label_fields_declared": True,
            "metadata_fields_declared": True,
            "metadata_only": True,
            "payload_free": True,
        },
        "sample_ready": False,
        "model_use_enabled": False,
    }
    validate_openssl_model_sequence_sample_contract(contract)
    return contract


def validate_openssl_model_sequence_sample_contract(contract: dict[str, Any]) -> None:
    """Validate an OpenSSL model-sequence sample contract."""

    _require_equal(contract.get("format"), OPENSSL_MODEL_SEQUENCE_SAMPLE_CONTRACT_FORMAT, "format")
    _require_equal(contract.get("status"), "sample_contract_ready", "status")
    _require_equal(contract.get("phase"), "P16", "phase")
    _require_equal(contract.get("target"), "openssl_model_sequence_sample", "target")
    _require_equal(contract.get("mode"), "contract_only", "mode")
    _require_non_empty_string(contract.get("input_manifest_format"), "input_manifest_format")
    _require_non_empty_string(contract.get("input_contract_format"), "input_contract_format")
    _require_non_empty_string(contract.get("input_digest"), "input_digest")
    _require_non_empty_string(contract.get("source_pin_digest"), "source_pin_digest")
    _require_non_empty_string(contract.get("trace_contract_digest"), "trace_contract_digest")
    _require_non_empty_string(contract.get("feature_namespace"), "feature_namespace")
    _require_non_empty_string(contract.get("sample_id"), "sample_id")
    _require_non_empty_string_list(contract.get("feature_fields"), "feature_fields")
    _require_non_empty_string_list(contract.get("label_fields"), "label_fields")
    _require_non_empty_string_list(contract.get("metadata_fields"), "metadata_fields")
    schema = _require_dict(contract.get("sample_schema"), "sample_schema")
    for flag in SAMPLE_CONTRACT_FLAGS:
        if flag not in schema:
            raise OpenSSLModelSequenceSampleContractError(f"sample_schema missing: {flag}")
        if not isinstance(schema[flag], bool):
            raise OpenSSLModelSequenceSampleContractError(f"sample_schema.{flag} must be a bool")
        _require_equal(schema[flag], True, f"sample_schema.{flag}")
    _require_equal(contract.get("sample_ready"), False, "sample_ready")
    _require_equal(contract.get("model_use_enabled"), False, "model_use_enabled")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceSampleContractError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceSampleContractError(f"{name} must be a non-empty string")
    return value


def _require_non_empty_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise OpenSSLModelSequenceSampleContractError(f"{name} must be a non-empty list")
    for item in value:
        _require_non_empty_string(item, f"{name} item")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceSampleContractError(f"{name} must be {expected!r}")
