"""OpenSSL materialization output contract helpers."""

from __future__ import annotations

from typing import Any

from traceleak.openssl_materialization_approval_gate import (
    validate_openssl_materialization_approval_gate,
)

OPENSSL_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT = (
    "traceleak.openssl_materialization_output_contract.v1"
)
OUTPUT_SCHEMA_FLAGS = [
    "digest_required",
    "manifest_required",
    "redacted_metadata_only",
    "source_text_embedded",
    "diff_embedded",
    "commands_embedded",
    "build_output_embedded",
    "execution_output_embedded",
    "raw_capture_embedded",
]


class OpenSSLMaterializationOutputContractError(ValueError):
    """Raised when an OpenSSL materialization output contract is invalid."""


def build_openssl_materialization_output_contract(
    *,
    approval_gate: dict[str, Any],
    output_manifest_path: str,
) -> dict[str, Any]:
    """Build a contract for future OpenSSL materialization output metadata."""

    validate_openssl_materialization_approval_gate(approval_gate)
    contract = {
        "format": OPENSSL_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT,
        "status": "output_contract_ready",
        "phase": "P10",
        "target": "openssl_materialization_output",
        "mode": "contract_only",
        "source_pin_digest": approval_gate["source_pin_digest"],
        "trace_contract_digest": approval_gate["trace_contract_digest"],
        "workspace_root": approval_gate["workspace_root"],
        "approval_scope": approval_gate["approval_scope"],
        "output_manifest_path": output_manifest_path,
        "output_schema": {
            "digest_required": True,
            "manifest_required": True,
            "redacted_metadata_only": True,
            "source_text_embedded": False,
            "diff_embedded": False,
            "commands_embedded": False,
            "build_output_embedded": False,
            "execution_output_embedded": False,
            "raw_capture_embedded": False,
        },
        "output_generated": False,
        "patch_application_allowed": False,
        "compile_allowed": False,
        "execution_allowed": False,
        "raw_capture_allowed": False,
    }
    validate_openssl_materialization_output_contract(contract)
    return contract


def validate_openssl_materialization_output_contract(contract: dict[str, Any]) -> None:
    """Validate an OpenSSL materialization output contract."""

    _require_equal(contract.get("format"), OPENSSL_MATERIALIZATION_OUTPUT_CONTRACT_FORMAT, "format")
    _require_equal(contract.get("status"), "output_contract_ready", "status")
    _require_equal(contract.get("phase"), "P10", "phase")
    _require_equal(contract.get("target"), "openssl_materialization_output", "target")
    _require_equal(contract.get("mode"), "contract_only", "mode")
    _require_non_empty_string(contract.get("source_pin_digest"), "source_pin_digest")
    _require_non_empty_string(contract.get("trace_contract_digest"), "trace_contract_digest")
    _require_non_empty_string(contract.get("workspace_root"), "workspace_root")
    _require_non_empty_string(contract.get("approval_scope"), "approval_scope")
    _require_non_empty_string(contract.get("output_manifest_path"), "output_manifest_path")
    schema = _require_dict(contract.get("output_schema"), "output_schema")
    for flag in OUTPUT_SCHEMA_FLAGS:
        if flag not in schema:
            raise OpenSSLMaterializationOutputContractError(f"output_schema missing: {flag}")
        if not isinstance(schema[flag], bool):
            raise OpenSSLMaterializationOutputContractError(f"output_schema.{flag} must be a bool")
    _require_equal(schema["digest_required"], True, "output_schema.digest_required")
    _require_equal(schema["manifest_required"], True, "output_schema.manifest_required")
    _require_equal(schema["redacted_metadata_only"], True, "output_schema.redacted_metadata_only")
    _require_equal(schema["source_text_embedded"], False, "output_schema.source_text_embedded")
    _require_equal(schema["diff_embedded"], False, "output_schema.diff_embedded")
    _require_equal(schema["commands_embedded"], False, "output_schema.commands_embedded")
    _require_equal(schema["build_output_embedded"], False, "output_schema.build_output_embedded")
    _require_equal(schema["execution_output_embedded"], False, "output_schema.execution_output_embedded")
    _require_equal(schema["raw_capture_embedded"], False, "output_schema.raw_capture_embedded")
    _require_equal(contract.get("output_generated"), False, "output_generated")
    _require_equal(contract.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(contract.get("compile_allowed"), False, "compile_allowed")
    _require_equal(contract.get("execution_allowed"), False, "execution_allowed")
    _require_equal(contract.get("raw_capture_allowed"), False, "raw_capture_allowed")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLMaterializationOutputContractError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLMaterializationOutputContractError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLMaterializationOutputContractError(f"{name} must be {expected!r}")
