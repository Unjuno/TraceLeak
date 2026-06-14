"""Adapter for public-safe OpenSSL-derived metadata records."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from traceleak.openssl_runtime_transition_gate import validate_openssl_runtime_transition_gate

OPENSSL_DERIVED_METADATA_INPUT_FORMAT = "traceleak.openssl_derived_metadata_input.v1"
OPENSSL_DERIVED_METADATA_MODEL_SEQUENCE_FORMAT = "traceleak.openssl_derived_metadata_model_sequence.v1"
FORBIDDEN_FIELDS = {
    "source_text",
    "diff_text",
    "command_text",
    "build_output",
    "execution_output",
    "raw_capture",
    "payload",
    "private_key",
    "value_raw",
}


class OpenSSLDerivedMetadataAdapterError(ValueError):
    """Raised when OpenSSL-derived metadata cannot be adapted safely."""


def adapt_openssl_derived_metadata_to_model_sequence(
    *,
    metadata_input: dict[str, Any],
    runtime_gate: dict[str, Any],
) -> dict[str, Any]:
    """Convert public-safe OpenSSL-derived metadata into model-sequence records."""

    validate_openssl_runtime_transition_gate(runtime_gate)
    validate_openssl_derived_metadata_input(metadata_input)
    records = []
    for index, item in enumerate(metadata_input["records"]):
        region = str(item["source_region_token"])
        transition = str(item["transition_token"])
        label = str(item.get("label", "candidate"))
        counts = {
            f"region:{region}": 1.0,
            f"transition:{transition}": 1.0,
            f"target:{metadata_input['target_decision']}": 1.0,
        }
        records.append(
            {
                "run_id": str(item.get("run_id", f"openssl-derived-{index:04d}")),
                "target": "openssl-derived-metadata",
                "target_version": metadata_input["source_pin_digest"],
                "view": "meta",
                "sequence": [
                    {
                        "event_token": f"region:{region}",
                        "source_token": "openssl.derived.symbolic",
                        "context_token": f"target:{metadata_input['target_decision']}",
                        "event_type": "metadata",
                        "phase": "openssl_derived_metadata",
                    },
                    {
                        "event_token": f"transition:{transition}",
                        "source_token": "openssl.derived.symbolic",
                        "context_token": f"record_index:{index}",
                        "event_type": "metadata",
                        "phase": "openssl_derived_metadata",
                    },
                ],
                "token_counts": counts,
                "label": label,
                "metadata": {
                    "metadata_only": True,
                    "payload_free": True,
                    "source_region_token": region,
                },
            }
        )
    payload = {
        "format": "traceleak.model_sequence.v1",
        "artifact_format": OPENSSL_DERIVED_METADATA_MODEL_SEQUENCE_FORMAT,
        "input_format": metadata_input["format"],
        "target": "openssl-derived-metadata",
        "view": "meta",
        "run_count": len(records),
        "public_safe": True,
        "include_counts": True,
        "include_redacted_values": False,
        "label_name": metadata_input.get("label_name", "label"),
        "contains_lab_only_labels": True,
        "records": records,
        "notes": [
            "OpenSSL-derived metadata adapter output; symbolic metadata only.",
            "No OpenSSL source text, command text, build output, execution output, raw capture, or runtime payload is embedded.",
        ],
    }
    validate_openssl_derived_metadata_model_sequence(payload)
    return payload


def validate_openssl_derived_metadata_input(metadata_input: dict[str, Any]) -> None:
    _reject_forbidden(metadata_input, "metadata_input")
    _eq(metadata_input.get("format"), OPENSSL_DERIVED_METADATA_INPUT_FORMAT, "format")
    _non_empty(metadata_input.get("source_pin_digest"), "source_pin_digest")
    _eq(metadata_input.get("target_decision"), "constant_time_helper_misuse_path", "target_decision")
    _eq(metadata_input.get("metadata_only"), True, "metadata_only")
    _eq(metadata_input.get("payload_free"), True, "payload_free")
    records = metadata_input.get("records")
    if not isinstance(records, list) or not records:
        raise OpenSSLDerivedMetadataAdapterError("records must be a non-empty list")
    label_counts: Counter[str] = Counter()
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise OpenSSLDerivedMetadataAdapterError(f"records[{index}] must be an object")
        _reject_forbidden(item, f"records[{index}]")
        _non_empty(item.get("source_region_token"), f"records[{index}].source_region_token")
        _non_empty(item.get("transition_token"), f"records[{index}].transition_token")
        label_counts[str(item.get("label", "candidate"))] += 1
    if len(label_counts) < 2:
        raise OpenSSLDerivedMetadataAdapterError("records must contain at least two labels")


def validate_openssl_derived_metadata_model_sequence(payload: dict[str, Any]) -> None:
    _eq(payload.get("format"), "traceleak.model_sequence.v1", "format")
    _eq(payload.get("artifact_format"), OPENSSL_DERIVED_METADATA_MODEL_SEQUENCE_FORMAT, "artifact_format")
    _eq(payload.get("target"), "openssl-derived-metadata", "target")
    _eq(payload.get("view"), "meta", "view")
    _eq(payload.get("public_safe"), True, "public_safe")
    _eq(payload.get("include_counts"), True, "include_counts")
    _eq(payload.get("include_redacted_values"), False, "include_redacted_values")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise OpenSSLDerivedMetadataAdapterError("records must be a non-empty list")
    _eq(payload.get("run_count"), len(records), "run_count")
    _reject_forbidden(payload, "payload")


def write_openssl_derived_metadata_model_sequence(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _reject_forbidden(value: Any, name: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_FIELDS:
                raise OpenSSLDerivedMetadataAdapterError(f"{name} must not contain {key}")
            _reject_forbidden(child, f"{name}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden(child, f"{name}[{index}]")


def _non_empty(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise OpenSSLDerivedMetadataAdapterError(f"{name} must be a non-empty string")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLDerivedMetadataAdapterError(f"{name} must be {expected!r}")
