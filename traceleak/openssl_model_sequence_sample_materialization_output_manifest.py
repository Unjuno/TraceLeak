"""OpenSSL model-sequence sample materialization output manifest helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_model_sequence_sample_materialization_output_contract import (
    OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT,
    validate_openssl_model_sequence_sample_materialization_output_contract,
)

OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_FORMAT = (
    "traceleak.openssl_model_sequence_sample_materialization_output_manifest.v1"
)
SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_TRUE_FLAGS = [
    "output_contract_bound",
    "request_contract_bound",
    "digest_recorded",
    "metadata_only",
    "payload_free",
]
SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_FALSE_FLAGS = [
    "sample_artifact_generated",
    "model_use_enabled",
    "model_training_allowed",
    "runtime_action_enabled",
    "payload_access_enabled",
]


class OpenSSLModelSequenceSampleMaterializationOutputManifestError(ValueError):
    """Raised when a sample materialization output manifest is invalid."""


def build_openssl_model_sequence_sample_materialization_output_manifest(
    *,
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
    artifact_digests: dict[str, str],
) -> dict[str, Any]:
    """Build a metadata-only manifest shell for future sample materialization output."""

    validate_openssl_model_sequence_sample_materialization_output_contract(
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    manifest = {
        "format": OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_FORMAT,
        "status": "sample_materialization_output_manifest_ready",
        "phase": "P21",
        "target": "openssl_model_sequence_sample_materialization_output_manifest",
        "mode": "metadata_only",
        "output_contract_format": (
            OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT
        ),
        "request_contract_format": output_contract["request_contract_format"],
        "sample_manifest_format": output_contract["sample_manifest_format"],
        "approval_gate_format": output_contract["approval_gate_format"],
        "input_digest": output_contract["input_digest"],
        "sample_digest": output_contract["sample_digest"],
        "source_pin_digest": output_contract["source_pin_digest"],
        "trace_contract_digest": output_contract["trace_contract_digest"],
        "feature_namespace": output_contract["feature_namespace"],
        "sample_id": output_contract["sample_id"],
        "planned_sample_path": output_contract["planned_sample_path"],
        "output_manifest_path": output_contract["output_manifest_path"],
        "artifact_digests": dict(artifact_digests),
        "metadata": {
            "output_contract_bound": True,
            "request_contract_bound": True,
            "digest_recorded": True,
            "metadata_only": True,
            "payload_free": True,
            "sample_artifact_generated": False,
            "model_use_enabled": False,
            "model_training_allowed": False,
            "runtime_action_enabled": False,
            "payload_access_enabled": False,
        },
    }
    validate_openssl_model_sequence_sample_materialization_output_manifest(
        manifest=manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    return manifest


def validate_openssl_model_sequence_sample_materialization_output_manifest(
    *,
    manifest: dict[str, Any],
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
) -> None:
    """Validate a metadata-only sample materialization output manifest shell."""

    validate_openssl_model_sequence_sample_materialization_output_contract(
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    _require_equal(
        manifest.get("format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_FORMAT,
        "format",
    )
    _require_equal(
        manifest.get("status"),
        "sample_materialization_output_manifest_ready",
        "status",
    )
    _require_equal(manifest.get("phase"), "P21", "phase")
    _require_equal(
        manifest.get("target"),
        "openssl_model_sequence_sample_materialization_output_manifest",
        "target",
    )
    _require_equal(manifest.get("mode"), "metadata_only", "mode")
    _require_equal(
        manifest.get("output_contract_format"),
        OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT,
        "output_contract_format",
    )
    for field in [
        "request_contract_format",
        "sample_manifest_format",
        "approval_gate_format",
        "input_digest",
        "sample_digest",
        "source_pin_digest",
        "trace_contract_digest",
        "feature_namespace",
        "sample_id",
        "planned_sample_path",
        "output_manifest_path",
    ]:
        _require_equal(manifest.get(field), output_contract[field], field)
    artifact_digests = _require_dict(manifest.get("artifact_digests"), "artifact_digests")
    if not artifact_digests:
        raise OpenSSLModelSequenceSampleMaterializationOutputManifestError(
            "artifact_digests must be non-empty"
        )
    for name, digest in artifact_digests.items():
        _require_non_empty_string(name, "artifact_digests key")
        _require_non_empty_string(digest, f"artifact_digests.{name}")
    _require_metadata(manifest)


def _require_metadata(candidate: dict[str, Any]) -> None:
    metadata = _require_dict(candidate.get("metadata"), "metadata")
    for flag in SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_TRUE_FLAGS:
        if flag not in metadata:
            raise OpenSSLModelSequenceSampleMaterializationOutputManifestError(
                f"metadata missing: {flag}"
            )
        _require_equal(metadata[flag], True, f"metadata.{flag}")
    for flag in SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_FALSE_FLAGS:
        if flag not in metadata:
            raise OpenSSLModelSequenceSampleMaterializationOutputManifestError(
                f"metadata missing: {flag}"
            )
        _require_equal(metadata[flag], False, f"metadata.{flag}")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceSampleMaterializationOutputManifestError(
            f"{name} must be an object"
        )
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceSampleMaterializationOutputManifestError(
            f"{name} must be a non-empty string"
        )
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceSampleMaterializationOutputManifestError(
            f"{name} must be {expected!r}"
        )
