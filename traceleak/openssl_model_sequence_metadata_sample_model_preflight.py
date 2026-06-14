"""OpenSSL metadata-only model-sequence sample model preflight helpers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from traceleak.baselines import label_distribution
from traceleak.model_sequence_nn import parse_model_sequence_nn_vectors
from traceleak.openssl_model_sequence_metadata_sample import (
    OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_ARTIFACT_FORMAT,
    validate_openssl_model_sequence_metadata_sample,
)

OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_MODEL_PREFLIGHT_FORMAT = (
    "traceleak.openssl_model_sequence_metadata_sample_model_preflight.v1"
)
MODEL_PREFLIGHT_TRUE_FLAGS = [
    "metadata_only",
    "payload_free",
    "public_safe",
    "baseline_input_compatible",
    "nn_input_compatible",
    "leave_one_out_ready",
]
MODEL_PREFLIGHT_FALSE_FLAGS = [
    "baseline_result_generated",
    "model_result_generated",
    "model_use_enabled",
    "model_training_allowed",
    "runtime_action_enabled",
    "payload_access_enabled",
]


class OpenSSLModelSequenceMetadataSampleModelPreflightError(ValueError):
    """Raised when a metadata-only sample model preflight is invalid."""


def build_openssl_model_sequence_metadata_sample_model_preflight(
    *,
    sample: dict[str, Any],
    output_manifest: dict[str, Any],
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build a preflight proving the metadata sample is baseline/NN input compatible."""

    validate_openssl_model_sequence_metadata_sample(
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    vectors = parse_model_sequence_nn_vectors(sample)
    label_counts = Counter(vector.label for vector in vectors)
    feature_names = sorted(
        {
            name
            for vector in vectors
            for name, value in vector.features.items()
            if value != 0.0
        }
    )
    preflight = {
        "format": OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_MODEL_PREFLIGHT_FORMAT,
        "status": "metadata_sample_model_preflight_ready",
        "phase": "P23",
        "target": "openssl_model_sequence_metadata_sample_model_preflight",
        "mode": "preflight_only",
        "input_format": sample["format"],
        "artifact_format": OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_ARTIFACT_FORMAT,
        "sample_id": sample["sample_metadata"]["sample_id"],
        "input_digest": sample["sample_metadata"]["input_digest"],
        "sample_digest": sample["sample_metadata"]["sample_digest"],
        "source_pin_digest": sample["sample_metadata"]["source_pin_digest"],
        "trace_contract_digest": sample["sample_metadata"]["trace_contract_digest"],
        "feature_namespace": sample["sample_metadata"]["feature_namespace"],
        "planned_sample_path": sample["sample_metadata"]["planned_sample_path"],
        "output_manifest_path": sample["sample_metadata"]["output_manifest_path"],
        "record_count": len(vectors),
        "label_name": sample["label_name"],
        "label_distribution": label_distribution(vectors),
        "label_count": len(label_counts),
        "feature_count": len(feature_names),
        "preflight": {
            "metadata_only": True,
            "payload_free": True,
            "public_safe": True,
            "baseline_input_compatible": True,
            "nn_input_compatible": True,
            "leave_one_out_ready": True,
            "baseline_result_generated": False,
            "model_result_generated": False,
            "model_use_enabled": False,
            "model_training_allowed": False,
            "runtime_action_enabled": False,
            "payload_access_enabled": False,
        },
        "notes": [
            "Preflight only: confirms the metadata-only sample can be parsed as model-sequence token counts.",
            "No baseline result, neural model result, OpenSSL runtime action, or payload access is produced here.",
            "Synthetic lab-only labels are for public pipeline checks, not OpenSSL leakage claims.",
        ],
    }
    validate_openssl_model_sequence_metadata_sample_model_preflight(
        preflight=preflight,
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    return preflight


def validate_openssl_model_sequence_metadata_sample_model_preflight(
    *,
    preflight: dict[str, Any],
    sample: dict[str, Any],
    output_manifest: dict[str, Any],
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
) -> None:
    """Validate a metadata-only sample model preflight."""

    validate_openssl_model_sequence_metadata_sample(
        sample=sample,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    vectors = parse_model_sequence_nn_vectors(sample)
    label_counts = Counter(vector.label for vector in vectors)
    feature_names = {
        name
        for vector in vectors
        for name, value in vector.features.items()
        if value != 0.0
    }
    _require_equal(
        preflight.get("format"),
        OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_MODEL_PREFLIGHT_FORMAT,
        "format",
    )
    _require_equal(preflight.get("status"), "metadata_sample_model_preflight_ready", "status")
    _require_equal(preflight.get("phase"), "P23", "phase")
    _require_equal(
        preflight.get("target"),
        "openssl_model_sequence_metadata_sample_model_preflight",
        "target",
    )
    _require_equal(preflight.get("mode"), "preflight_only", "mode")
    _require_equal(preflight.get("input_format"), sample["format"], "input_format")
    _require_equal(
        preflight.get("artifact_format"),
        OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_ARTIFACT_FORMAT,
        "artifact_format",
    )
    _require_sample_binding(preflight, sample)
    _require_equal(preflight.get("record_count"), len(vectors), "record_count")
    _require_equal(preflight.get("label_name"), sample["label_name"], "label_name")
    _require_equal(preflight.get("label_distribution"), label_distribution(vectors), "label_distribution")
    _require_equal(preflight.get("label_count"), len(label_counts), "label_count")
    _require_equal(preflight.get("feature_count"), len(feature_names), "feature_count")
    if len(label_counts) < 2:
        raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
            "preflight requires at least two labels"
        )
    if any(count < 2 for count in label_counts.values()):
        raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
            "preflight requires at least two examples per label"
        )
    if not feature_names:
        raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
            "preflight requires at least one token feature"
        )
    _require_flags(preflight)
    notes = _require_non_empty_list(preflight.get("notes"), "notes")
    for index, note in enumerate(notes):
        _require_non_empty_string(note, f"notes[{index}]")


def write_openssl_model_sequence_metadata_sample_model_preflight(
    path: Path,
    preflight: dict[str, Any],
) -> None:
    """Write a metadata-only sample model preflight as deterministic JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(preflight, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_sample_binding(preflight: dict[str, Any], sample: dict[str, Any]) -> None:
    metadata = _require_dict(sample.get("sample_metadata"), "sample_metadata")
    for field in [
        "sample_id",
        "input_digest",
        "sample_digest",
        "source_pin_digest",
        "trace_contract_digest",
        "feature_namespace",
        "planned_sample_path",
        "output_manifest_path",
    ]:
        _require_equal(preflight.get(field), metadata[field], field)


def _require_flags(preflight: dict[str, Any]) -> None:
    flags = _require_dict(preflight.get("preflight"), "preflight")
    for flag in MODEL_PREFLIGHT_TRUE_FLAGS:
        if flag not in flags:
            raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
                f"preflight missing: {flag}"
            )
        _require_equal(flags[flag], True, f"preflight.{flag}")
    for flag in MODEL_PREFLIGHT_FALSE_FLAGS:
        if flag not in flags:
            raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
                f"preflight missing: {flag}"
            )
        _require_equal(flags[flag], False, f"preflight.{flag}")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
            f"{name} must be an object"
        )
    return value


def _require_non_empty_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
            f"{name} must be a non-empty list"
        )
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
            f"{name} must be a non-empty string"
        )
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceMetadataSampleModelPreflightError(
            f"{name} must be {expected!r}"
        )
