"""OpenSSL model-sequence input manifest helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_input_contract import (
    validate_openssl_model_sequence_input_contract,
)

OPENSSL_MODEL_SEQUENCE_INPUT_MANIFEST_FORMAT = "traceleak.openssl_model_sequence_input_manifest.v1"
INPUT_MANIFEST_FLAGS = [
    "contract_bound",
    "artifact_digests_bound",
    "metadata_only",
    "payload_free",
]


class OpenSSLModelSequenceInputManifestError(ValueError):
    """Raised when an OpenSSL model-sequence input manifest is invalid."""


def build_openssl_model_sequence_input_manifest(
    *,
    input_contract: dict[str, Any],
    input_digest: str,
) -> dict[str, Any]:
    """Build a metadata-only manifest for a future model-sequence input."""

    validate_openssl_model_sequence_input_contract(input_contract)
    manifest = {
        "format": OPENSSL_MODEL_SEQUENCE_INPUT_MANIFEST_FORMAT,
        "status": "input_manifest_ready",
        "phase": "P15",
        "target": "openssl_model_sequence_input_manifest",
        "mode": "metadata_only",
        "contract_format": input_contract["format"],
        "source_pin_digest": input_contract["source_pin_digest"],
        "trace_contract_digest": input_contract["trace_contract_digest"],
        "artifact_digests": dict(input_contract["artifact_digests"]),
        "feature_namespace": input_contract["feature_namespace"],
        "sample_id": input_contract["sample_id"],
        "output_sample_path": input_contract["output_sample_path"],
        "input_digest": input_digest,
        "manifest_schema": {
            "contract_bound": True,
            "artifact_digests_bound": True,
            "metadata_only": True,
            "payload_free": True,
        },
        "input_ready": False,
        "model_use_enabled": False,
    }
    validate_openssl_model_sequence_input_manifest(
        manifest=manifest,
        input_contract=input_contract,
    )
    return manifest


def validate_openssl_model_sequence_input_manifest(
    *,
    manifest: dict[str, Any],
    input_contract: dict[str, Any],
) -> None:
    """Validate a metadata-only model-sequence input manifest."""

    validate_openssl_model_sequence_input_contract(input_contract)
    _require_equal(manifest.get("format"), OPENSSL_MODEL_SEQUENCE_INPUT_MANIFEST_FORMAT, "format")
    _require_equal(manifest.get("status"), "input_manifest_ready", "status")
    _require_equal(manifest.get("phase"), "P15", "phase")
    _require_equal(manifest.get("target"), "openssl_model_sequence_input_manifest", "target")
    _require_equal(manifest.get("mode"), "metadata_only", "mode")
    _require_equal(manifest.get("contract_format"), input_contract["format"], "contract_format")
    _require_equal(manifest.get("source_pin_digest"), input_contract["source_pin_digest"], "source_pin_digest")
    _require_equal(
        manifest.get("trace_contract_digest"),
        input_contract["trace_contract_digest"],
        "trace_contract_digest",
    )
    _require_equal(manifest.get("feature_namespace"), input_contract["feature_namespace"], "feature_namespace")
    _require_equal(manifest.get("sample_id"), input_contract["sample_id"], "sample_id")
    _require_equal(
        manifest.get("output_sample_path"),
        input_contract["output_sample_path"],
        "output_sample_path",
    )
    _require_non_empty_string(manifest.get("input_digest"), "input_digest")
    artifact_digests = _require_dict(manifest.get("artifact_digests"), "artifact_digests")
    _require_equal(artifact_digests, input_contract["artifact_digests"], "artifact_digests")
    schema = _require_dict(manifest.get("manifest_schema"), "manifest_schema")
    for flag in INPUT_MANIFEST_FLAGS:
        if flag not in schema:
            raise OpenSSLModelSequenceInputManifestError(f"manifest_schema missing: {flag}")
        if not isinstance(schema[flag], bool):
            raise OpenSSLModelSequenceInputManifestError(f"manifest_schema.{flag} must be a bool")
        _require_equal(schema[flag], True, f"manifest_schema.{flag}")
    _require_equal(manifest.get("input_ready"), False, "input_ready")
    _require_equal(manifest.get("model_use_enabled"), False, "model_use_enabled")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceInputManifestError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceInputManifestError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceInputManifestError(f"{name} must be {expected!r}")
