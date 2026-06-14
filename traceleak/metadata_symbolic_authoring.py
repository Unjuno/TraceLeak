"""Authoring helpers for metadata-only symbolic records."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from traceleak.openssl_derived_metadata_adapter import (
    OPENSSL_DERIVED_METADATA_INPUT_FORMAT,
    validate_openssl_derived_metadata_input,
)

SYMBOLIC_METADATA_AUTHORING_PHASE = "P80"
DEFAULT_TARGET_DECISION = "constant_time_helper_misuse_path"
FORBIDDEN_AUTHORING_FIELDS = {
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


class MetadataSymbolicAuthoringError(ValueError):
    """Raised when symbolic metadata authoring input is invalid."""


def build_symbolic_metadata_input(
    *,
    records: list[dict[str, Any]],
    source_pin_digest: str = "sha256:source-pin",
    label_name: str = "metadata_bucket",
    target_decision: str = DEFAULT_TARGET_DECISION,
) -> dict[str, Any]:
    """Build a metadata-only symbolic input object for the existing adapter."""

    _non_empty(source_pin_digest, "source_pin_digest")
    _non_empty(label_name, "label_name")
    _eq(target_decision, DEFAULT_TARGET_DECISION, "target_decision")
    authored_records = _build_records(records)
    payload = {
        "format": OPENSSL_DERIVED_METADATA_INPUT_FORMAT,
        "authoring_phase": SYMBOLIC_METADATA_AUTHORING_PHASE,
        "source_pin_digest": source_pin_digest,
        "target_decision": target_decision,
        "metadata_only": True,
        "payload_free": True,
        "label_name": label_name,
        "records": authored_records,
    }
    validate_symbolic_metadata_input(payload)
    return payload


def validate_symbolic_metadata_input(payload: dict[str, Any]) -> None:
    """Validate authored symbolic metadata before adapter use."""

    _reject_forbidden(payload, "payload")
    _eq(payload.get("format"), OPENSSL_DERIVED_METADATA_INPUT_FORMAT, "format")
    _eq(payload.get("authoring_phase"), SYMBOLIC_METADATA_AUTHORING_PHASE, "authoring_phase")
    _eq(payload.get("target_decision"), DEFAULT_TARGET_DECISION, "target_decision")
    _eq(payload.get("metadata_only"), True, "metadata_only")
    _eq(payload.get("payload_free"), True, "payload_free")
    _non_empty(payload.get("source_pin_digest"), "source_pin_digest")
    _non_empty(payload.get("label_name"), "label_name")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) < 4:
        raise MetadataSymbolicAuthoringError("records must contain at least four entries")
    label_counts: Counter[str] = Counter()
    seen_run_ids: set[str] = set()
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise MetadataSymbolicAuthoringError(f"records[{index}] must be an object")
        _reject_forbidden(item, f"records[{index}]")
        _non_empty(item.get("run_id"), f"records[{index}].run_id")
        _non_empty(item.get("source_region_token"), f"records[{index}].source_region_token")
        _non_empty(item.get("transition_token"), f"records[{index}].transition_token")
        _non_empty(item.get("label"), f"records[{index}].label")
        if item["run_id"] in seen_run_ids:
            raise MetadataSymbolicAuthoringError("run_id values must be unique")
        seen_run_ids.add(item["run_id"])
        label_counts[item["label"]] += 1
    if len(label_counts) < 2:
        raise MetadataSymbolicAuthoringError("records must contain at least two labels")
    if min(label_counts.values()) < 2:
        raise MetadataSymbolicAuthoringError("each label must have at least two records")
    validate_openssl_derived_metadata_input(payload)


def write_symbolic_metadata_input(path: Path, payload: dict[str, Any]) -> None:
    """Write authored symbolic metadata input as deterministic JSON."""

    validate_symbolic_metadata_input(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_records(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    if not isinstance(records, list):
        raise MetadataSymbolicAuthoringError("records must be a list")
    output = []
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise MetadataSymbolicAuthoringError(f"records[{index}] must be an object")
        _reject_forbidden(item, f"records[{index}]")
        region = item.get("source_region_token")
        transition = item.get("transition_token")
        label = item.get("label")
        _non_empty(region, f"records[{index}].source_region_token")
        _non_empty(transition, f"records[{index}].transition_token")
        _non_empty(label, f"records[{index}].label")
        output.append(
            {
                "run_id": str(item.get("run_id", f"symbolic-{index:04d}")),
                "source_region_token": str(region),
                "transition_token": str(transition),
                "label": str(label),
            }
        )
    return output


def _reject_forbidden(value: Any, name: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_AUTHORING_FIELDS:
                raise MetadataSymbolicAuthoringError(f"{name} must not contain {key}")
            _reject_forbidden(child, f"{name}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden(child, f"{name}[{index}]")


def _non_empty(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise MetadataSymbolicAuthoringError(f"{name} must be a non-empty string")


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise MetadataSymbolicAuthoringError(f"{name} must be {expected!r}")
