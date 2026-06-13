"""OpenSSL materialization output manifest helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_materialization_output_contract import (
    validate_openssl_materialization_output_contract,
)

OPENSSL_MATERIALIZATION_OUTPUT_MANIFEST_FORMAT = (
    "traceleak.openssl_materialization_output_manifest.v1"
)
MANIFEST_METADATA_FLAGS = [
    "redacted_metadata_only",
    "source_text_embedded",
    "diff_embedded",
    "commands_embedded",
    "build_output_embedded",
    "execution_output_embedded",
    "raw_capture_embedded",
]


class OpenSSLMaterializationOutputManifestError(ValueError):
    """Raised when an OpenSSL materialization output manifest is invalid."""


def build_openssl_materialization_output_manifest(
    *,
    output_contract: dict[str, Any],
    artifact_digests: dict[str, str],
) -> dict[str, Any]:
    """Build a redacted metadata-only OpenSSL materialization output manifest."""

    validate_openssl_materialization_output_contract(output_contract)
    manifest = {
        "format": OPENSSL_MATERIALIZATION_OUTPUT_MANIFEST_FORMAT,
        "status": "manifest_ready",
        "phase": "P11",
        "target": "openssl_materialization_output_manifest",
        "mode": "metadata_only",
        "contract_format": output_contract["format"],
        "source_pin_digest": output_contract["source_pin_digest"],
        "trace_contract_digest": output_contract["trace_contract_digest"],
        "workspace_root": output_contract["workspace_root"],
        "output_manifest_path": output_contract["output_manifest_path"],
        "artifact_digests": dict(artifact_digests),
        "metadata": {
            "redacted_metadata_only": True,
            "source_text_embedded": False,
            "diff_embedded": False,
            "commands_embedded": False,
            "build_output_embedded": False,
            "execution_output_embedded": False,
            "raw_capture_embedded": False,
        },
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_materialization_output_manifest(
        manifest=manifest,
        output_contract=output_contract,
    )
    return manifest


def validate_openssl_materialization_output_manifest(
    *,
    manifest: dict[str, Any],
    output_contract: dict[str, Any],
) -> None:
    """Validate a redacted metadata-only OpenSSL materialization output manifest."""

    validate_openssl_materialization_output_contract(output_contract)
    _require_equal(manifest.get("format"), OPENSSL_MATERIALIZATION_OUTPUT_MANIFEST_FORMAT, "format")
    _require_equal(manifest.get("status"), "manifest_ready", "status")
    _require_equal(manifest.get("phase"), "P11", "phase")
    _require_equal(manifest.get("target"), "openssl_materialization_output_manifest", "target")
    _require_equal(manifest.get("mode"), "metadata_only", "mode")
    _require_equal(manifest.get("contract_format"), output_contract["format"], "contract_format")
    _require_equal(
        manifest.get("source_pin_digest"),
        output_contract["source_pin_digest"],
        "source_pin_digest",
    )
    _require_equal(
        manifest.get("trace_contract_digest"),
        output_contract["trace_contract_digest"],
        "trace_contract_digest",
    )
    _require_equal(manifest.get("workspace_root"), output_contract["workspace_root"], "workspace_root")
    _require_equal(
        manifest.get("output_manifest_path"),
        output_contract["output_manifest_path"],
        "output_manifest_path",
    )
    artifact_digests = _require_dict(manifest.get("artifact_digests"), "artifact_digests")
    if not artifact_digests:
        raise OpenSSLMaterializationOutputManifestError("artifact_digests must be non-empty")
    for name, digest in artifact_digests.items():
        _require_non_empty_string(name, "artifact_digests key")
        _require_non_empty_string(digest, f"artifact_digests.{name}")
    metadata = _require_dict(manifest.get("metadata"), "metadata")
    for flag in MANIFEST_METADATA_FLAGS:
        if flag not in metadata:
            raise OpenSSLMaterializationOutputManifestError(f"metadata missing: {flag}")
        if not isinstance(metadata[flag], bool):
            raise OpenSSLMaterializationOutputManifestError(f"metadata.{flag} must be a bool")
    _require_equal(metadata["redacted_metadata_only"], True, "metadata.redacted_metadata_only")
    _require_equal(metadata["source_text_embedded"], False, "metadata.source_text_embedded")
    _require_equal(metadata["diff_embedded"], False, "metadata.diff_embedded")
    _require_equal(metadata["commands_embedded"], False, "metadata.commands_embedded")
    _require_equal(metadata["build_output_embedded"], False, "metadata.build_output_embedded")
    _require_equal(metadata["execution_output_embedded"], False, "metadata.execution_output_embedded")
    _require_equal(metadata["raw_capture_embedded"], False, "metadata.raw_capture_embedded")
    _require_equal(manifest.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(manifest.get("compile_allowed"), False, "compile_allowed")
    _require_equal(manifest.get("execution_allowed"), False, "execution_allowed")
    _require_equal(manifest.get("raw_capture_allowed"), False, "raw_capture_allowed")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLMaterializationOutputManifestError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLMaterializationOutputManifestError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLMaterializationOutputManifestError(f"{name} must be {expected!r}")
