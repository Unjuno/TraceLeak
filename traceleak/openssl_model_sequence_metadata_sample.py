"""OpenSSL metadata-only model-sequence sample helpers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from traceleak.openssl_model_sequence_sample_materialization_output_manifest import (
    OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_FORMAT,
    validate_openssl_model_sequence_sample_materialization_output_manifest,
)

OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_ARTIFACT_FORMAT = (
    "traceleak.openssl_model_sequence_metadata_sample.v1"
)
MODEL_SEQUENCE_FORMAT = "traceleak.model_sequence.v1"
OPENSSL_METADATA_SAMPLE_TARGET = "openssl-metadata-only"
OPENSSL_METADATA_SAMPLE_VIEW = "metadata_only"
FORBIDDEN_METADATA_SAMPLE_FIELDS = [
    "source_text",
    "diff_text",
    "command_text",
    "build_output",
    "execution_output",
    "raw_capture",
    "payload",
]


class OpenSSLModelSequenceMetadataSampleError(ValueError):
    """Raised when an OpenSSL metadata-only model-sequence sample is invalid."""


def build_openssl_model_sequence_metadata_sample(
    *,
    output_manifest: dict[str, Any],
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
    record_count: int = 4,
    label_name: str = "metadata_probe_bucket",
) -> dict[str, Any]:
    """Build a public-safe metadata-only model-sequence sample artifact."""

    _validate_parent_chain(
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    if not isinstance(record_count, int) or record_count < 4:
        raise OpenSSLModelSequenceMetadataSampleError("record_count must be an integer >= 4")
    if record_count % 2 != 0:
        raise OpenSSLModelSequenceMetadataSampleError("record_count must be even")
    _require_non_empty_string(label_name, "label_name")

    records = [
        _build_record(
            output_manifest=output_manifest,
            index=index,
            label_name=label_name,
        )
        for index in range(record_count)
    ]
    payload = {
        "format": MODEL_SEQUENCE_FORMAT,
        "artifact_format": OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_ARTIFACT_FORMAT,
        "input": output_manifest["output_manifest_path"],
        "target": OPENSSL_METADATA_SAMPLE_TARGET,
        "view": OPENSSL_METADATA_SAMPLE_VIEW,
        "run_count": len(records),
        "public_safe": True,
        "include_counts": True,
        "include_redacted_values": False,
        "label_name": label_name,
        "contains_lab_only_labels": True,
        "sample_metadata": {
            "source": "openssl_model_sequence_metadata_sample",
            "phase": "P22",
            "metadata_only": True,
            "payload_free": True,
            "sample_artifact_generated": True,
            "model_use_enabled": False,
            "model_training_allowed": False,
            "runtime_action_enabled": False,
            "payload_access_enabled": False,
            "output_manifest_format": (
                OPENSSL_MODEL_SEQUENCE_SAMPLE_MATERIALIZATION_OUTPUT_MANIFEST_FORMAT
            ),
            "sample_id": output_manifest["sample_id"],
            "input_digest": output_manifest["input_digest"],
            "sample_digest": output_manifest["sample_digest"],
            "source_pin_digest": output_manifest["source_pin_digest"],
            "trace_contract_digest": output_manifest["trace_contract_digest"],
            "feature_namespace": output_manifest["feature_namespace"],
            "planned_sample_path": output_manifest["planned_sample_path"],
            "output_manifest_path": output_manifest["output_manifest_path"],
        },
        "records": records,
        "notes": [
            "Metadata-only OpenSSL model-sequence sample generated for public pipeline checks.",
            "This artifact contains no OpenSSL source text, command text, build output, execution output, raw capture, or runtime payload.",
            "Labels are synthetic lab-only metadata probe buckets; they are not evidence of OpenSSL leakage.",
        ],
    }
    validate_openssl_model_sequence_metadata_sample(
        sample=payload,
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    return payload


def validate_openssl_model_sequence_metadata_sample(
    *,
    sample: dict[str, Any],
    output_manifest: dict[str, Any],
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
) -> None:
    """Validate a public-safe metadata-only model-sequence sample artifact."""

    _validate_parent_chain(
        output_manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )
    _reject_forbidden_fields(sample, "sample")
    _require_equal(sample.get("format"), MODEL_SEQUENCE_FORMAT, "format")
    _require_equal(
        sample.get("artifact_format"),
        OPENSSL_MODEL_SEQUENCE_METADATA_SAMPLE_ARTIFACT_FORMAT,
        "artifact_format",
    )
    _require_equal(sample.get("input"), output_manifest["output_manifest_path"], "input")
    _require_equal(sample.get("target"), OPENSSL_METADATA_SAMPLE_TARGET, "target")
    _require_equal(sample.get("view"), OPENSSL_METADATA_SAMPLE_VIEW, "view")
    _require_equal(sample.get("public_safe"), True, "public_safe")
    _require_equal(sample.get("include_counts"), True, "include_counts")
    _require_equal(sample.get("include_redacted_values"), False, "include_redacted_values")
    _require_equal(sample.get("contains_lab_only_labels"), True, "contains_lab_only_labels")
    label_name = _require_non_empty_string(sample.get("label_name"), "label_name")
    records = _require_non_empty_list(sample.get("records"), "records")
    _require_equal(sample.get("run_count"), len(records), "run_count")
    _require_sample_metadata(sample, output_manifest)
    _require_records(records, label_name=label_name)
    notes = _require_non_empty_list(sample.get("notes"), "notes")
    for index, note in enumerate(notes):
        _require_non_empty_string(note, f"notes[{index}]")


def write_openssl_model_sequence_metadata_sample(path: Path, sample: dict[str, Any]) -> None:
    """Write a metadata-only model-sequence sample artifact as deterministic JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_record(
    *,
    output_manifest: dict[str, Any],
    index: int,
    label_name: str,
) -> dict[str, Any]:
    bucket = "even" if index % 2 == 0 else "odd"
    sample_id = str(output_manifest["sample_id"])
    run_id = f"{sample_id}-metadata-{index:04d}"
    base_counts = {
        "meta:target:openssl": 1.0,
        f"meta:feature_namespace:{output_manifest['feature_namespace']}": 1.0,
        f"meta:sample_id:{sample_id}": 1.0,
        f"lab_probe_bucket:{bucket}": 1.0,
    }
    sequence = [
        _step(
            event_token="metadata_sample_start",
            source_token="openssl.metadata_sample.public",
            context_token=f"sample_id:{sample_id}",
            phase="metadata_sample",
        ),
        _step(
            event_token=f"metadata_probe_bucket:{bucket}",
            source_token="openssl.metadata_sample.lab_only",
            context_token=f"record_index:{index}",
            phase="metadata_probe",
        ),
    ]
    return {
        "run_id": run_id,
        "target": OPENSSL_METADATA_SAMPLE_TARGET,
        "target_version": output_manifest["source_pin_digest"],
        "view": OPENSSL_METADATA_SAMPLE_VIEW,
        "sequence": sequence,
        "token_counts": base_counts,
        "label": f"metadata_{bucket}",
        "metadata": {
            "sample_id": sample_id,
            "record_index": index,
            "label_name": label_name,
            "metadata_only": True,
            "payload_free": True,
        },
    }


def _step(
    *,
    event_token: str,
    source_token: str,
    context_token: str,
    phase: str,
) -> dict[str, str]:
    return {
        "event_token": event_token,
        "source_token": source_token,
        "context_token": context_token,
        "event_type": "metadata",
        "phase": phase,
    }


def _validate_parent_chain(
    *,
    output_manifest: dict[str, Any],
    output_contract: dict[str, Any],
    sample_manifest: dict[str, Any],
    approval_record: dict[str, Any],
    approval_gate: dict[str, Any],
    request_contract: dict[str, Any],
) -> None:
    validate_openssl_model_sequence_sample_materialization_output_manifest(
        manifest=output_manifest,
        output_contract=output_contract,
        sample_manifest=sample_manifest,
        approval_record=approval_record,
        approval_gate=approval_gate,
        request_contract=request_contract,
    )


def _require_sample_metadata(sample: dict[str, Any], output_manifest: dict[str, Any]) -> None:
    metadata = _require_dict(sample.get("sample_metadata"), "sample_metadata")
    _reject_forbidden_fields(metadata, "sample_metadata")
    _require_equal(metadata.get("phase"), "P22", "sample_metadata.phase")
    _require_equal(metadata.get("metadata_only"), True, "sample_metadata.metadata_only")
    _require_equal(metadata.get("payload_free"), True, "sample_metadata.payload_free")
    _require_equal(
        metadata.get("sample_artifact_generated"),
        True,
        "sample_metadata.sample_artifact_generated",
    )
    for flag in [
        "model_use_enabled",
        "model_training_allowed",
        "runtime_action_enabled",
        "payload_access_enabled",
    ]:
        _require_equal(metadata.get(flag), False, f"sample_metadata.{flag}")
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
        _require_equal(metadata.get(field), output_manifest[field], f"sample_metadata.{field}")


def _require_records(records: list[Any], *, label_name: str) -> None:
    label_counts: Counter[str] = Counter()
    for index, record in enumerate(records):
        record_dict = _require_dict(record, f"records[{index}]")
        _reject_forbidden_fields(record_dict, f"records[{index}]")
        _require_non_empty_string(record_dict.get("run_id"), f"records[{index}].run_id")
        _require_equal(record_dict.get("target"), OPENSSL_METADATA_SAMPLE_TARGET, f"records[{index}].target")
        _require_non_empty_string(record_dict.get("target_version"), f"records[{index}].target_version")
        _require_equal(record_dict.get("view"), OPENSSL_METADATA_SAMPLE_VIEW, f"records[{index}].view")
        label = _require_non_empty_string(record_dict.get("label"), f"records[{index}].label")
        label_counts[label] += 1
        token_counts = _require_dict(record_dict.get("token_counts"), f"records[{index}].token_counts")
        if not token_counts:
            raise OpenSSLModelSequenceMetadataSampleError(
                f"records[{index}].token_counts must be non-empty"
            )
        for name, value in token_counts.items():
            _require_non_empty_string(name, f"records[{index}].token_counts key")
            if not isinstance(value, int | float) or value <= 0:
                raise OpenSSLModelSequenceMetadataSampleError(
                    f"records[{index}].token_counts.{name} must be a positive number"
                )
        sequence = _require_non_empty_list(record_dict.get("sequence"), f"records[{index}].sequence")
        for step_index, step in enumerate(sequence):
            _require_step(step, record_index=index, step_index=step_index)
        metadata = _require_dict(record_dict.get("metadata"), f"records[{index}].metadata")
        _require_equal(metadata.get("label_name"), label_name, f"records[{index}].metadata.label_name")
        _require_equal(metadata.get("metadata_only"), True, f"records[{index}].metadata.metadata_only")
        _require_equal(metadata.get("payload_free"), True, f"records[{index}].metadata.payload_free")
    if len(label_counts) < 2:
        raise OpenSSLModelSequenceMetadataSampleError("records must contain at least two labels")
    rare = sorted(label for label, count in label_counts.items() if count < 2)
    if rare:
        raise OpenSSLModelSequenceMetadataSampleError(
            "records must contain at least two examples per label"
        )


def _require_step(step: Any, *, record_index: int, step_index: int) -> None:
    step_dict = _require_dict(step, f"records[{record_index}].sequence[{step_index}]")
    for field in ["event_token", "source_token", "context_token", "event_type", "phase"]:
        _require_non_empty_string(
            step_dict.get(field),
            f"records[{record_index}].sequence[{step_index}].{field}",
        )


def _reject_forbidden_fields(candidate: dict[str, Any], name: str) -> None:
    for field in FORBIDDEN_METADATA_SAMPLE_FIELDS:
        if field in candidate:
            raise OpenSSLModelSequenceMetadataSampleError(f"{name} must not contain {field}")


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLModelSequenceMetadataSampleError(f"{name} must be an object")
    return value


def _require_non_empty_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise OpenSSLModelSequenceMetadataSampleError(f"{name} must be a non-empty list")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLModelSequenceMetadataSampleError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLModelSequenceMetadataSampleError(f"{name} must be {expected!r}")
