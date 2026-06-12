"""Build OpenSSL model_sequence.v1 samples from redacted TraceLeak event runs.

The builder consumes already-collected redacted run records and emits the
model-sequence token-count sample expected by the OpenSSL acceptance gate. It
does not build, run, instrument, or trace OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.model_features import ModelFeatureError, sequence_token_counts, trace_to_model_sequence
from traceleak.openssl_trace_acceptance import validate_openssl_trace_sample_acceptance
from traceleak.openssl_trace_contract import MODEL_SEQUENCE_FORMAT, OpenSSLTraceContractError, validate_openssl_trace_contract
from traceleak.openssl_trace_event_stream import (
    OpenSSLTraceEventStreamError,
    load_openssl_redacted_event_stream,
    validate_openssl_redacted_event_stream,
)
from traceleak.schema import TraceSchemaError, validate_run


class OpenSSLTraceSampleBuilderError(ValueError):
    """Raised when OpenSSL redacted event runs cannot be converted safely."""


def load_redacted_event_runs(path: str | Path) -> list[dict[str, Any]]:
    """Load redacted TraceLeak run dictionaries from a JSONL file."""

    try:
        return load_openssl_redacted_event_stream(path)
    except OpenSSLTraceEventStreamError as exc:
        raise OpenSSLTraceSampleBuilderError(str(exc)) from exc


def build_openssl_model_sequence_sample(
    *,
    contract: dict[str, Any],
    runs: list[dict[str, Any]],
    input_name: str,
    label_key: str | None = None,
) -> dict[str, Any]:
    """Build and acceptance-validate a model_sequence.v1 sample from redacted OpenSSL runs."""

    try:
        validate_openssl_trace_contract(contract)
        validate_openssl_redacted_event_stream(contract, runs)
    except (OpenSSLTraceContractError, OpenSSLTraceEventStreamError) as exc:
        raise OpenSSLTraceSampleBuilderError(str(exc)) from exc
    if not runs:
        raise OpenSSLTraceSampleBuilderError("at least one run is required")

    effective_label_key = label_key or _single_allowed_label_key(contract)
    records = [
        _build_record(contract=contract, run=run, index=index, label_key=effective_label_key)
        for index, run in enumerate(runs, start=1)
    ]
    sample: dict[str, Any] = {
        "format": MODEL_SEQUENCE_FORMAT,
        "input": input_name,
        "run_count": len(records),
        "public_safe": True,
        "include_counts": True,
        "include_redacted_values": False,
        "label_name": effective_label_key,
        "contains_lab_only_labels": True,
        "target": contract["target"],
        "target_version": contract["target_version"],
        "source_pin": contract["source_pin"],
        "build_id": contract["build_id"],
        "view": "redacted",
        "validation_scope": "actual_trace_derived",
        "actual_trace_derived": True,
        "trace_collection_mode": "redacted",
        "raw_secret_captured": False,
        "notes": [
            "Built from redacted TraceLeak event runs; raw secret capture is not allowed.",
            "This builder does not build, run, instrument, or trace OpenSSL.",
        ],
        "records": records,
    }
    try:
        validate_openssl_trace_sample_acceptance(contract, sample)
    except ValueError as exc:
        raise OpenSSLTraceSampleBuilderError(str(exc)) from exc
    return sample


def write_model_sequence_sample(path: str | Path, sample: dict[str, Any]) -> None:
    """Write a model_sequence.v1 sample JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_record(
    *,
    contract: dict[str, Any],
    run: dict[str, Any],
    index: int,
    label_key: str,
) -> dict[str, Any]:
    try:
        validate_run(run, public_export=True)
    except TraceSchemaError as exc:
        run_id = run.get("run_id", f"record_{index}")
        raise OpenSSLTraceSampleBuilderError(f"run {run_id!r} is invalid: {exc}") from exc
    _require_equal(run.get("target"), contract["target"], f"runs[{index}].target")
    _require_equal(run.get("target_version"), contract["target_version"], f"runs[{index}].target_version")
    _require_equal(run.get("view"), "redacted", f"runs[{index}].view")
    try:
        sequence = trace_to_model_sequence(run, allow_raw=False, include_redacted_values=False)
    except (TraceSchemaError, ModelFeatureError) as exc:
        raise OpenSSLTraceSampleBuilderError(f"run {run['run_id']!r} cannot be encoded: {exc}") from exc
    return {
        "run_id": run["run_id"],
        "target": run["target"],
        "target_version": run["target_version"],
        "view": run["view"],
        "label": _label_from_run(run, label_key),
        "token_counts": sequence_token_counts(sequence),
    }


def _single_allowed_label_key(contract: dict[str, Any]) -> str:
    labels = contract["labels"]["allowed_label_keys"]
    if len(labels) != 1:
        raise OpenSSLTraceSampleBuilderError("label_key is required when contract allows multiple labels")
    return str(labels[0])


def _label_from_run(run: dict[str, Any], label_key: str) -> str:
    labels = run.get("labels_lab_only")
    if not isinstance(labels, dict):
        raise OpenSSLTraceSampleBuilderError(f"run {run['run_id']!r} has no labels_lab_only object")
    if label_key not in labels:
        raise OpenSSLTraceSampleBuilderError(f"run {run['run_id']!r} is missing labels_lab_only.{label_key}")
    return str(labels[label_key])


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLTraceSampleBuilderError(f"{name} must be {expected!r}")
