"""OpenSSL metadata demo manifest validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.model_results import validate_model_result
from traceleak.openssl_model_sequence_metadata_sample_demo_result import (
    OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_DEMO_RESULT_FORMAT,
    validate_openssl_model_sequence_metadata_sample_demo_result,
)

OPENSSL_MODEL_SEQUENCE_METADATA_DEMO_MANIFEST_FORMAT = (
    "traceleak.openssl_model_sequence_metadata_demo_manifest.v1"
)


class OpenSSLModelSequenceMetadataDemoManifestError(ValueError):
    """Raised when an OpenSSL metadata demo manifest is invalid."""


def build_openssl_model_sequence_metadata_demo_manifest(
    *,
    summary: dict[str, Any],
    baseline_result: dict[str, Any],
    nn_result: dict[str, Any],
    sample: dict[str, Any],
    model_preflight: dict[str, Any],
) -> dict[str, Any]:
    """Build a manifest for P24 metadata-only demo outputs."""

    validate_openssl_model_sequence_metadata_sample_demo_result(
        summary=summary,
        baseline_result=baseline_result,
        nn_result=nn_result,
        sample=sample,
        model_preflight=model_preflight,
    )
    manifest = {
        "format": OPENSSL_MODEL_SEQUENCE_METADATA_DEMO_MANIFEST_FORMAT,
        "status": "metadata_demo_manifest_ready",
        "phase": "P26",
        "target": "openssl_model_sequence_metadata_demo_manifest",
        "mode": "metadata_only_demo_manifest",
        "demo_result_format": OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_DEMO_RESULT_FORMAT,
        "sample_id": summary["sample_id"],
        "input_digest": summary["input_digest"],
        "sample_digest": summary["sample_digest"],
        "source_pin_digest": summary["source_pin_digest"],
        "trace_contract_digest": summary["trace_contract_digest"],
        "feature_namespace": summary["feature_namespace"],
        "record_count": summary["record_count"],
        "label_distribution": summary["label_distribution"],
        "baseline_result_type": baseline_result["result_type"],
        "nn_result_type": nn_result["result_type"],
        "public_statement": {
            "metadata_only": True,
            "payload_free": True,
            "public_safe": True,
            "openssl_leakage_claim": False,
            "runtime_action_enabled": False,
            "payload_access_enabled": False,
        },
        "notes": [
            "P26 manifest validates P24 public demo outputs.",
            "This manifest does not represent an OpenSSL leakage finding.",
        ],
    }
    validate_openssl_model_sequence_metadata_demo_manifest(
        manifest=manifest,
        summary=summary,
        baseline_result=baseline_result,
        nn_result=nn_result,
        sample=sample,
        model_preflight=model_preflight,
    )
    return manifest


def validate_openssl_model_sequence_metadata_demo_manifest(
    *,
    manifest: dict[str, Any],
    summary: dict[str, Any],
    baseline_result: dict[str, Any],
    nn_result: dict[str, Any],
    sample: dict[str, Any],
    model_preflight: dict[str, Any],
) -> None:
    """Validate a P26 metadata-only demo manifest."""

    validate_openssl_model_sequence_metadata_sample_demo_result(
        summary=summary,
        baseline_result=baseline_result,
        nn_result=nn_result,
        sample=sample,
        model_preflight=model_preflight,
    )
    validate_model_result(nn_result)
    _eq(manifest.get("format"), OPENSSL_MODEL_SEQUENCE_METADATA_DEMO_MANIFEST_FORMAT, "format")
    _eq(manifest.get("status"), "metadata_demo_manifest_ready", "status")
    _eq(manifest.get("phase"), "P26", "phase")
    _eq(manifest.get("target"), "openssl_model_sequence_metadata_demo_manifest", "target")
    _eq(manifest.get("mode"), "metadata_only_demo_manifest", "mode")
    _eq(manifest.get("demo_result_format"), summary["format"], "demo_result_format")
    for field in [
        "sample_id",
        "input_digest",
        "sample_digest",
        "source_pin_digest",
        "trace_contract_digest",
        "feature_namespace",
        "record_count",
        "label_distribution",
    ]:
        _eq(manifest.get(field), summary[field], field)
    _eq(manifest.get("baseline_result_type"), "model_sequence_baseline", "baseline_result_type")
    _eq(manifest.get("nn_result_type"), "model_sequence_nn", "nn_result_type")
    statement = _dict(manifest.get("public_statement"), "public_statement")
    for flag in ["metadata_only", "payload_free", "public_safe"]:
        _eq(statement.get(flag), True, f"public_statement.{flag}")
    for flag in ["openssl_leakage_claim", "runtime_action_enabled", "payload_access_enabled"]:
        _eq(statement.get(flag), False, f"public_statement.{flag}")


def write_openssl_model_sequence_metadata_demo_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceMetadataDemoManifestError(f"{name} must be an object")
    return value


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceMetadataDemoManifestError(f"{name} must be {expected!r}")
