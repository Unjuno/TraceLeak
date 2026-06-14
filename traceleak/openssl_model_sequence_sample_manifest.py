"""OpenSSL model-sequence sample manifest helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_sample_contract import (
    validate_openssl_model_sequence_sample_contract,
)

OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT = "traceleak.openssl_model_sequence_sample_manifest.v1"
SAMPLE_MANIFEST_FLAGS = [
    "contract_bound",
    "feature_fields_bound",
    "label_fields_bound",
    "metadata_fields_bound",
    "metadata_only",
    "payload_free",
]


class OpenSSLModelSequenceSampleManifestError(ValueError):
    """Raised when an OpenSSL model-sequence sample manifest is invalid."""


def build_openssl_model_sequence_sample_manifest(
    *,
    sample_contract: dict[str, Any],
    sample_digest: str,
) -> dict[str, Any]:
    """Build a metadata-only manifest for a future model-sequence sample."""

    validate_openssl_model_sequence_sample_contract(sample_contract)
    manifest = {
        "format": OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT,
        "status": "sample_manifest_ready",
        "phase": "P17",
        "target": "openssl_model_sequence_sample_manifest",
        "mode": "metadata_only",
        "sample_contract_format": sample_contract["format"],
        "input_digest": sample_contract["input_digest"],
        "sample_digest": sample_digest,
        "source_pin_digest": sample_contract["source_pin_digest"],
        "trace_contract_digest": sample_contract["trace_contract_digest"],
        "feature_namespace": sample_contract["feature_namespace"],
        "sample_id": sample_contract["sample_id"],
        "feature_fields": list(sample_contract["feature_fields"]),
        "label_fields": list(sample_contract["label_fields"]),
        "metadata_fields": list(sample_contract["metadata_fields"]),
        "manifest_schema": {
            "contract_bound": True,
            "feature_fields_bound": True,
            "label_fields_bound": True,
            "metadata_fields_bound": True,
            "metadata_only": True,
            "payload_free": True,
        },
        "sample_ready": False,
        "model_use_enabled": False,
    }
    validate_openssl_model_sequence_sample_manifest(
        manifest=manifest,
        sample_contract=sample_contract,
    )
    return manifest


def validate_openssl_model_sequence_sample_manifest(
    *,
    manifest: dict[str, Any],
    sample_contract: dict[str, Any],
) -> None:
    """Validate a metadata-only model-sequence sample manifest."""

    validate_openssl_model_sequence_sample_contract(sample_contract)
    _require_equal(manifest.get("format"), OPENSSL_MODEL_SEQUENCE_SAMPLE_MANIFEST_FORMAT, "format")
    _require_equal(manifest.get("status"), "sample_manifest_ready", "status")
    _require_equal(manifest.get("phase"), "P17", "phase")
    _require_equal(manifest.get("target"), "openssl_model_sequence_sample_manifest", "target")
    _require_equal(manifest.get("mode"), "metadata_only", "mode")
    _require_equal(
        manifest.get("sample_contract_format"),
        sample_contract["format"],
        "sample_contract_format",
    )
    _require_equal(manifest.get("input_digest"), sample_contract["input_digest"], "input_digest")
    _require_non_empty_string(manifest.get("sample_digest"), "sample_digest")
    _require_equal(
        manifest.get("source_pin_digest"),
        sample_contract["source_pin_digest"],
        "source_pin_digest",
    )
    _require_equal(
        manifest.get("trace_contract_digest"),
        sample_contract["trace_contract_digest"],
        "trace_contract_digest",
    )
    _require_equal(
        manifest.get("feature_namespace"),
        sample_contract["feature_namespace"],
        "feature_namespace",
    )
    _require_equal(manifest.get("sample_id"), sample_contract["sample_id"], "sample_id")
    _require_equal(manifest.get("feature_fields"), sample_contract["feature_fields"], "feature_fields")
    _require_equal(manifest.get("label_fields"), sample_contract["label_fields"], "label_fields")
    _require_equal(
        manifest.get("metadata_fields"),
        sample_contract["metadata_fields"],
        "metadata_fields",
    )
    schema = _require_dict(manifest.get("manifest_schema"), "manifest_schema")
    for flag in SAMPLE_MANIFEST_FLAGS:
        if flag not in schema:
            raise OpenSSLModelSequenceSampleManifestError(f"manifest_schema missing: {flag}")
        if not isinstance(schema[flag], bool):
            raise OpenSSLModelSequenceSampleManifestError(f"manifest_schema.{flag} must be a bool")
        _require_equal(schema[flag], True, f"manifest_schema.{flag}")
    _require_equal(manifest.get("sample_ready"), False, "sample_ready")
    _require_equal(manifest.get("model_use_enabled"), False, "model_use_enabled")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceSampleManifestError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceSampleManifestError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceSampleManifestError(f"{name} must be {expected!r}")
