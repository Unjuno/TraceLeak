"""Validate OpenSSL redacted TraceLeak event streams.

This module validates already-collected JSONL run records before they are
collapsed into model_sequence.v1 token-count samples. It does not build, run,
instrument, or trace OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_trace_contract import OpenSSLTraceContractError, validate_openssl_trace_contract
from traceleak.schema import TraceSchemaError, validate_run


class OpenSSLTraceEventStreamError(ValueError):
    """Raised when an OpenSSL redacted event stream is invalid."""


def load_openssl_redacted_event_stream(path: str | Path) -> list[dict[str, Any]]:
    """Load OpenSSL redacted TraceLeak run records from a JSONL file."""

    input_path = Path(path)
    if not input_path.exists():
        raise OpenSSLTraceEventStreamError(f"redacted event stream not found: {input_path}")
    runs: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                run = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise OpenSSLTraceEventStreamError(
                    f"{input_path}:{line_number}: invalid JSON: {exc}"
                ) from exc
            if not isinstance(run, dict):
                raise OpenSSLTraceEventStreamError(
                    f"{input_path}:{line_number}: each JSONL record must be an object"
                )
            runs.append(run)
    if not runs:
        raise OpenSSLTraceEventStreamError(f"no redacted event runs found in {input_path}")
    return runs


def validate_openssl_redacted_event_stream(contract: dict[str, Any], runs: list[dict[str, Any]]) -> None:
    """Validate a redacted event stream against an OpenSSL trace contract."""

    try:
        validate_openssl_trace_contract(contract)
    except OpenSSLTraceContractError as exc:
        raise OpenSSLTraceEventStreamError(str(exc)) from exc
    if not runs:
        raise OpenSSLTraceEventStreamError("at least one run is required")
    disallowed_fields = set(contract["safety"]["disallowed_fields"])
    allowed_label_keys = set(contract["labels"]["allowed_label_keys"])
    for index, run in enumerate(runs, start=1):
        _validate_run_against_contract(
            contract=contract,
            run=run,
            index=index,
            disallowed_fields=disallowed_fields,
            allowed_label_keys=allowed_label_keys,
        )


def openssl_redacted_event_stream_report_dict(
    contract: dict[str, Any], runs: list[dict[str, Any]]
) -> dict[str, Any]:
    """Build a normalized report for a redacted OpenSSL event stream."""

    validate_openssl_redacted_event_stream(contract, runs)
    labels = sorted(
        {
            f"{label_key}={run['labels_lab_only'][label_key]}"
            for run in runs
            for label_key in contract["labels"]["allowed_label_keys"]
        }
    )
    event_count = sum(len(run["events"]) for run in runs)
    event_types = sorted({event["event_type"] for run in runs for event in run["events"]})
    functions = sorted({event["function"] for run in runs for event in run["events"]})
    return {
        "report_type": "openssl_redacted_event_stream_report",
        "status": "accepted_redacted_openssl_event_stream",
        "contract_id": contract["contract_id"],
        "target": contract["target"],
        "target_version": contract["target_version"],
        "source_pin": contract["source_pin"],
        "build_id": contract["build_id"],
        "trace_collection_mode": "redacted",
        "raw_secret_captured": False,
        "public_safe": True,
        "run_count": len(runs),
        "event_count": event_count,
        "event_types": event_types,
        "functions": functions,
        "labels": labels,
        "notes": [
            "Accepted stream is redacted TraceLeak event data only.",
            "Event stream acceptance does not prove leakage; it only validates the collection boundary.",
        ],
    }


def openssl_redacted_event_stream_report_markdown(report: dict[str, Any]) -> str:
    """Render a redacted OpenSSL event stream report as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Redacted Event Stream Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Contract: `{report['contract_id']}`",
        f"- Target: `{report['target']}`",
        f"- Target version: `{report['target_version']}`",
        f"- Source pin: `{report['source_pin']}`",
        f"- Build ID: `{report['build_id']}`",
        f"- Trace collection mode: `{report['trace_collection_mode']}`",
        f"- Raw secret captured: `{str(report['raw_secret_captured']).lower()}`",
        f"- Public safe: `{str(report['public_safe']).lower()}`",
        f"- Runs: `{report['run_count']}`",
        f"- Events: `{report['event_count']}`",
        "",
        "## Event Types",
        "",
    ]
    lines.extend(f"- `{event_type}`" for event_type in report["event_types"])
    lines.extend(["", "## Functions", ""])
    lines.extend(f"- `{function}`" for function in report["functions"])
    lines.extend(["", "## Labels", ""])
    lines.extend(f"- `{label}`" for label in report["labels"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in report["notes"])
    lines.append("")
    return "\n".join(lines)


def write_openssl_redacted_event_stream_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write a redacted OpenSSL event stream report as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_redacted_event_stream_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write a redacted OpenSSL event stream report as Markdown."""

    Path(path).write_text(openssl_redacted_event_stream_report_markdown(report), encoding="utf-8")


def _validate_run_against_contract(
    *,
    contract: dict[str, Any],
    run: dict[str, Any],
    index: int,
    disallowed_fields: set[str],
    allowed_label_keys: set[str],
) -> None:
    try:
        validate_run(run, public_export=True)
    except TraceSchemaError as exc:
        run_id = run.get("run_id", f"record_{index}")
        raise OpenSSLTraceEventStreamError(f"run {run_id!r} is invalid: {exc}") from exc
    run_name = f"runs[{index}]"
    _require_equal(run.get("target"), contract["target"], f"{run_name}.target")
    _require_equal(run.get("target_version"), contract["target_version"], f"{run_name}.target_version")
    _require_equal(run.get("view"), "redacted", f"{run_name}.view")
    metadata = _require_object(run.get("metadata", {}), f"{run_name}.metadata")
    _require_equal(metadata.get("source_pin"), contract["source_pin"], f"{run_name}.metadata.source_pin")
    _require_equal(metadata.get("build_id"), contract["build_id"], f"{run_name}.metadata.build_id")
    _require_equal(metadata.get("trace_collection_mode"), "redacted", f"{run_name}.metadata.trace_collection_mode")
    _require_equal(metadata.get("raw_secret_captured"), False, f"{run_name}.metadata.raw_secret_captured")
    _require_equal(metadata.get("public_safe"), True, f"{run_name}.metadata.public_safe")
    events = _require_list(run.get("events"), f"{run_name}.events", min_items=1)
    labels = _require_object(run.get("labels_lab_only"), f"{run_name}.labels_lab_only")
    missing_labels = sorted(key for key in allowed_label_keys if key not in labels)
    if missing_labels:
        raise OpenSSLTraceEventStreamError(
            f"{run_name}.labels_lab_only missing: {', '.join(missing_labels)}"
        )
    _reject_disallowed_names(run, disallowed_fields, path=run_name)
    for event_index, event in enumerate(events, start=1):
        _validate_event_shape(event, run_name=run_name, event_index=event_index)


def _validate_event_shape(event: Any, *, run_name: str, event_index: int) -> None:
    if not isinstance(event, dict):
        raise OpenSSLTraceEventStreamError(f"{run_name}.events[{event_index}] must be an object")
    if "value_raw" in event:
        raise OpenSSLTraceEventStreamError(f"{run_name}.events[{event_index}] must not include value_raw")
    if "value_redacted" in event and not isinstance(event["value_redacted"], dict):
        raise OpenSSLTraceEventStreamError(
            f"{run_name}.events[{event_index}].value_redacted must be an object when present"
        )


def _reject_disallowed_names(value: Any, disallowed_fields: set[str], *, path: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key).lower()
            for field in disallowed_fields:
                if field.lower() == key_text:
                    raise OpenSSLTraceEventStreamError(f"{path} contains disallowed field: {field}")
            _reject_disallowed_names(item, disallowed_fields, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_disallowed_names(item, disallowed_fields, path=f"{path}[{index}]")


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLTraceEventStreamError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLTraceEventStreamError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLTraceEventStreamError(f"{name} must contain at least {min_items} item(s)")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLTraceEventStreamError(f"{name} must be {expected!r}")
