"""OpenSSL model-sequence input contract helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_ingestion_preflight import (
    validate_openssl_model_sequence_ingestion_preflight,
)

OPENSSL_MODEL_SEQUENCE_INPUT_CONTRACT_FORMAT = "traceleak.openssl_model_sequence_input_contract.v1"
INPUT_CONTRACT_SCHEMA_FLAGS = [
    "preflight_blocker_free",
    "artifact_digests_bound",
    "feature_namespace_bound",
    "sample_id_bound",
    "metadata_only",
    "payload_free",
]


class OpenSSLModelSequenceInputContractError(ValueError):
    """Raised when an OpenSSL model-sequence input contract is invalid."""


def build_openssl_model_sequence_input_contract(
    *,
    ingestion_preflight: dict[str, Any],
    output_sample_path: str,
) -> dict[str, Any]:
    """Build a contract for future model-sequence input preparation."""

    validate_openssl_model_sequence_ingestion_preflight(ingestion_preflight)
    if ingestion_preflight["blockers"]:
        raise OpenSSLModelSequenceInputContractError("preflight blockers must be empty")
    contract = {
        "format": OPENSSL_MODEL_SEQUENCE_INPUT_CONTRACT_FORMAT,
        "status": "input_contract_ready",
        "phase": "P14",
        "target": "openssl_model_sequence_input",
        "mode": "contract_only",
        "preflight_format": ingestion_preflight["format"],
        "source_pin_digest": ingestion_preflight["source_pin_digest"],
        "trace_contract_digest": ingestion_preflight["trace_contract_digest"],
        "artifact_digests": dict(ingestion_preflight["artifact_digests"]),
        "feature_namespace": ingestion_preflight["feature_namespace"],
        "sample_id": ingestion_preflight["sample_id"],
        "output_sample_path": output_sample_path,
        "input_schema": {
            "preflight_blocker_free": True,
            "artifact_digests_bound": True,
            "feature_namespace_bound": True,
            "sample_id_bound": True,
            "metadata_only": True,
            "payload_free": True,
        },
        "input_ready": False,
        "model_use_enabled": False,
    }
    validate_openssl_model_sequence_input_contract(contract)
    return contract


def validate_openssl_model_sequence_input_contract(contract: dict[str, Any]) -> None:
    """Validate an OpenSSL model-sequence input contract."""

    _require_equal(contract.get("format"), OPENSSL_MODEL_SEQUENCE_INPUT_CONTRACT_FORMAT, "format")
    _require_equal(contract.get("status"), "input_contract_ready", "status")
    _require_equal(contract.get("phase"), "P14", "phase")
    _require_equal(contract.get("target"), "openssl_model_sequence_input", "target")
    _require_equal(contract.get("mode"), "contract_only", "mode")
    _require_non_empty_string(contract.get("preflight_format"), "preflight_format")
    _require_non_empty_string(contract.get("source_pin_digest"), "source_pin_digest")
    _require_non_empty_string(contract.get("trace_contract_digest"), "trace_contract_digest")
    artifact_digests = _require_dict(contract.get("artifact_digests"), "artifact_digests")
    if not artifact_digests:
        raise OpenSSLModelSequenceInputContractError("artifact_digests must be non-empty")
    for name, digest in artifact_digests.items():
        _require_non_empty_string(name, "artifact_digests key")
        _require_non_empty_string(digest, f"artifact_digests.{name}")
    _require_non_empty_string(contract.get("feature_namespace"), "feature_namespace")
    _require_non_empty_string(contract.get("sample_id"), "sample_id")
    _require_non_empty_string(contract.get("output_sample_path"), "output_sample_path")
    schema = _require_dict(contract.get("input_schema"), "input_schema")
    for flag in INPUT_CONTRACT_SCHEMA_FLAGS:
        if flag not in schema:
            raise OpenSSLModelSequenceInputContractError(f"input_schema missing: {flag}")
        if not isinstance(schema[flag], bool):
            raise OpenSSLModelSequenceInputContractError(f"input_schema.{flag} must be a bool")
        _require_equal(schema[flag], True, f"input_schema.{flag}")
    _require_equal(contract.get("input_ready"), False, "input_ready")
    _require_equal(contract.get("model_use_enabled"), False, "model_use_enabled")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceInputContractError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceInputContractError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceInputContractError(f"{name} must be {expected!r}")
