"""Acceptance gate for OpenSSL actual trace-derived model-sequence samples.

This module validates a generated model_sequence.v1 token-count sample against an
OpenSSL trace collector contract. It does not build, run, instrument, or trace
OpenSSL.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from traceleak.model_sequence_boundary import validate_model_sequence_sample_boundary
from traceleak.openssl_trace_contract import (
    MODEL_SEQUENCE_FORMAT,
    OpenSSLTraceContractError,
    load_openssl_trace_contract,
    validate_openssl_trace_contract,
)


class OpenSSLTraceAcceptanceError(ValueError):
    """Raised when a trace-derived model-sequence sample fails acceptance."""


def load_model_sequence_sample(path: str | Path) -> dict[str, Any]:
    """Load a model-sequence sample JSON file."""

    sample_path = Path(path)
    if not sample_path.exists():
        raise OpenSSLTraceAcceptanceError(f"model-sequence sample not found: {sample_path}")
    try:
        sample = json.loads(sample_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OpenSSLTraceAcceptanceError(f"invalid JSON in {sample_path}: {exc}") from exc
    if not isinstance(sample, dict):
        raise OpenSSLTraceAcceptanceError("model-sequence sample must be a JSON object")
    return sample


def load_contract_and_sample(contract_path: str | Path, sample_path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load an OpenSSL trace contract and candidate model-sequence sample."""

    try:
        contract = load_openssl_trace_contract(contract_path)
    except OpenSSLTraceContractError as exc:
        raise OpenSSLTraceAcceptanceError(str(exc)) from exc
    return contract, load_model_sequence_sample(sample_path)


def validate_openssl_trace_sample_acceptance(
    contract: dict[str, Any], sample: dict[str, Any]
) -> None:
    """Validate that a model-sequence sample satisfies an OpenSSL trace contract."""

    try:
        validate_openssl_trace_contract(contract)
    except OpenSSLTraceContractError as exc:
        raise OpenSSLTraceAcceptanceError(str(exc)) from exc
    _require_equal(sample.get("format"), MODEL_SEQUENCE_FORMAT, "sample.format")
    boundary = _validate_boundary(sample)
    _require_equal(boundary["actual_trace_derived"], True, "sample.actual_trace_derived")
    _require_equal(boundary["trace_collection_mode"], "redacted", "sample.trace_collection_mode")
    _require_equal(boundary["raw_secret_captured"], False, "sample.raw_secret_captured")
    _require_equal(boundary["public_safe"], True, "sample.public_safe")
    _require_equal(sample.get("target"), contract["target"], "sample.target")
    _require_equal(sample.get("target_version"), contract["target_version"], "sample.target_version")
    _require_equal(sample.get("source_pin"), contract["source_pin"], "sample.source_pin")
    _require_equal(sample.get("build_id"), contract["build_id"], "sample.build_id")
    _require_equal(sample.get("view"), "redacted", "sample.view")
    _require_equal(sample.get("include_redacted_values", False), False, "sample.include_redacted_values")

    records = _require_list(sample.get("records"), "sample.records", min_items=1)
    allowed_channels = set(contract["safety"]["allowed_value_channels"])
    disallowed_fields = set(contract["safety"]["disallowed_fields"])
    required_fields = set(contract["collector"]["required_record_fields"])
    allowed_label_keys = set(contract["labels"]["allowed_label_keys"])
    label_name = _require_string(sample.get("label_name"), "sample.label_name")
    if label_name not in allowed_label_keys:
        raise OpenSSLTraceAcceptanceError(
            f"sample.label_name must be one of: {', '.join(sorted(allowed_label_keys))}"
        )
    _reject_disallowed_names(sample, disallowed_fields, path="sample")
    for index, record in enumerate(records):
        _validate_record(
            record,
            index=index,
            contract=contract,
            required_fields=required_fields,
            allowed_channels=allowed_channels,
            disallowed_fields=disallowed_fields,
        )


def openssl_trace_sample_acceptance_report_dict(
    contract: dict[str, Any], sample: dict[str, Any]
) -> dict[str, Any]:
    """Build a normalized acceptance report for a candidate model-sequence sample."""

    validate_openssl_trace_sample_acceptance(contract, sample)
    records = sample["records"]
    labels = sorted({str(record["label"]) for record in records})
    feature_names = sorted(
        {
            str(name)
            for record in records
            for name, value in record["token_counts"].items()
            if float(value) != 0.0
        }
    )
    return {
        "report_type": "openssl_trace_sample_acceptance_report",
        "status": "accepted_redacted_model_sequence_sample",
        "contract_id": contract["contract_id"],
        "target": sample["target"],
        "target_version": sample["target_version"],
        "source_pin": sample["source_pin"],
        "build_id": sample["build_id"],
        "actual_trace_derived": sample["actual_trace_derived"],
        "trace_collection_mode": sample["trace_collection_mode"],
        "raw_secret_captured": sample["raw_secret_captured"],
        "public_safe": sample["public_safe"],
        "view": sample["view"],
        "label_name": sample["label_name"],
        "record_count": len(records),
        "label_count": len(labels),
        "labels": labels,
        "feature_count": len(feature_names),
        "allowed_value_channels": list(contract["safety"]["allowed_value_channels"]),
        "disallowed_fields": list(contract["safety"]["disallowed_fields"]),
        "notes": [
            "Accepted sample is redacted model-sequence token-count data only.",
            "Acceptance does not independently prove leakage; it only validates the data contract.",
        ],
    }


def openssl_trace_sample_acceptance_report_markdown(report: dict[str, Any]) -> str:
    """Render an OpenSSL trace sample acceptance report as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Trace Sample Acceptance Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Contract: `{report['contract_id']}`",
        f"- Target: `{report['target']}`",
        f"- Target version: `{report['target_version']}`",
        f"- Source pin: `{report['source_pin']}`",
        f"- Build ID: `{report['build_id']}`",
        f"- Actual trace derived: `{str(report['actual_trace_derived']).lower()}`",
        f"- Trace collection mode: `{report['trace_collection_mode']}`",
        f"- Raw secret captured: `{str(report['raw_secret_captured']).lower()}`",
        f"- Public safe: `{str(report['public_safe']).lower()}`",
        f"- View: `{report['view']}`",
        f"- Label: `{report['label_name']}`",
        f"- Records: `{report['record_count']}`",
        f"- Labels: `{report['label_count']}`",
        f"- Features: `{report['feature_count']}`",
        "",
        "## Labels",
        "",
    ]
    lines.extend(f"- `{label}`" for label in report["labels"])
    lines.extend(["", "## Allowed Value Channels", ""])
    lines.extend(f"- `{channel}`" for channel in report["allowed_value_channels"])
    lines.extend(["", "## Disallowed Fields", ""])
    lines.extend(f"- `{field}`" for field in report["disallowed_fields"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in report["notes"])
    lines.append("")
    return "\n".join(lines)


def write_openssl_trace_sample_acceptance_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write an OpenSSL trace sample acceptance report as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_trace_sample_acceptance_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write an OpenSSL trace sample acceptance report as Markdown."""

    Path(path).write_text(openssl_trace_sample_acceptance_report_markdown(report), encoding="utf-8")


def _validate_boundary(sample: dict[str, Any]) -> dict[str, Any]:
    try:
        return validate_model_sequence_sample_boundary(sample)
    except ValueError as exc:
        raise OpenSSLTraceAcceptanceError(str(exc)) from exc


def _validate_record(
    record: Any,
    *,
    index: int,
    contract: dict[str, Any],
    required_fields: set[str],
    allowed_channels: set[str],
    disallowed_fields: set[str],
) -> None:
    if not isinstance(record, dict):
        raise OpenSSLTraceAcceptanceError(f"sample.records[{index}] must be an object")
    missing = sorted(required_fields - set(record))
    if missing:
        raise OpenSSLTraceAcceptanceError(
            f"sample.records[{index}] missing required fields: {', '.join(missing)}"
        )
    _require_string(record.get("run_id"), f"sample.records[{index}].run_id")
    _require_equal(record.get("target"), contract["target"], f"sample.records[{index}].target")
    _require_equal(
        record.get("target_version"),
        contract["target_version"],
        f"sample.records[{index}].target_version",
    )
    _require_equal(record.get("view"), "redacted", f"sample.records[{index}].view")
    _require_string(record.get("label"), f"sample.records[{index}].label")
    counts = _require_object(record.get("token_counts"), f"sample.records[{index}].token_counts")
    if not counts:
        raise OpenSSLTraceAcceptanceError(f"sample.records[{index}].token_counts must be non-empty")
    _reject_disallowed_names(record, disallowed_fields, path=f"sample.records[{index}]")
    for name, value in counts.items():
        token = _require_string(name, f"sample.records[{index}].token_counts key")
        _validate_token_count_channel(token, allowed_channels, index=index)
        _reject_disallowed_token(token, disallowed_fields, index=index)
        _require_non_negative_finite_number(value, f"sample.records[{index}].token_counts[{token!r}]")


def _validate_token_count_channel(token: str, allowed_channels: set[str], *, index: int) -> None:
    channel = token.split("=", 1)[0]
    if channel not in allowed_channels:
        raise OpenSSLTraceAcceptanceError(
            f"sample.records[{index}].token_counts channel not allowed: {channel}"
        )


def _reject_disallowed_token(token: str, disallowed_fields: set[str], *, index: int) -> None:
    lowered = token.lower()
    segments = set(re.findall(r"[a-z0-9_]+", lowered))
    for field in disallowed_fields:
        lowered_field = field.lower()
        if len(lowered_field) <= 2:
            matched = lowered_field in segments
        else:
            matched = lowered_field in lowered
        if matched:
            raise OpenSSLTraceAcceptanceError(
                f"sample.records[{index}].token_counts contains disallowed token field: {field}"
            )


def _reject_disallowed_names(value: Any, disallowed_fields: set[str], *, path: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key).lower()
            for field in disallowed_fields:
                if field.lower() == key_text:
                    raise OpenSSLTraceAcceptanceError(f"{path} contains disallowed field: {field}")
            _reject_disallowed_names(item, disallowed_fields, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_disallowed_names(item, disallowed_fields, path=f"{path}[{index}]")


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLTraceAcceptanceError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLTraceAcceptanceError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLTraceAcceptanceError(f"{name} must contain at least {min_items} item(s)")
    return value


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLTraceAcceptanceError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLTraceAcceptanceError(f"{name} must be {expected!r}")


def _require_non_negative_finite_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise OpenSSLTraceAcceptanceError(f"{name} must be a number")
    if not math.isfinite(float(value)) or float(value) < 0.0:
        raise OpenSSLTraceAcceptanceError(f"{name} must be a non-negative finite number")
