"""OpenSSL actual trace-derived model-sequence collector contract.

This module validates the contract for a future local OpenSSL trace collection
step. It does not build, run, instrument, or trace OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OPENSSL_TRACE_CONTRACT_FORMAT = "traceleak.openssl_trace_contract.v1"
MODEL_SEQUENCE_FORMAT = "traceleak.model_sequence.v1"
REQUIRED_RECORD_FIELDS = {
    "run_id",
    "target",
    "target_version",
    "view",
    "label",
    "token_counts",
}
REQUIRED_DISALLOWED_FIELDS = {
    "p",
    "q",
    "d",
    "private_key",
    "raw_bignum",
    "prime_candidate",
    "seed",
    "rng_state",
}
REQUIRED_ALLOWED_VALUE_CHANNELS = {
    "event_token",
    "source_token",
    "context_token",
    "event_type",
    "phase",
    "count",
}
FORBIDDEN_ALLOWED_VALUE_CHANNELS = {
    "raw_secret",
    "raw_bignum",
    "private_key",
    "prime_candidate",
    "seed",
    "rng_state",
}
REQUIRED_CONTROLS = {
    "shuffled_label_negative_control",
    "public_only_baseline",
    "expected_token_ablation",
}


class OpenSSLTraceContractError(ValueError):
    """Raised when an OpenSSL trace collector contract is invalid."""


def load_openssl_trace_contract(path: str | Path) -> dict[str, Any]:
    """Load and validate an OpenSSL trace collector contract."""

    contract_path = Path(path)
    if not contract_path.exists():
        raise OpenSSLTraceContractError(f"OpenSSL trace contract not found: {contract_path}")
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OpenSSLTraceContractError(f"invalid JSON in {contract_path}: {exc}") from exc
    if not isinstance(contract, dict):
        raise OpenSSLTraceContractError("OpenSSL trace contract must be a JSON object")
    validate_openssl_trace_contract(contract)
    return contract


def validate_openssl_trace_contract(contract: dict[str, Any]) -> None:
    """Validate the local actual-trace-derived model-sequence contract."""

    _require_equal(contract.get("format"), OPENSSL_TRACE_CONTRACT_FORMAT, "format")
    _require_string(contract.get("contract_id"), "contract_id")
    _require_openssl_target(_require_string(contract.get("target"), "target"), "target")
    _require_openssl_target(
        _require_string(contract.get("target_family"), "target_family"), "target_family"
    )
    _require_string(contract.get("target_version"), "target_version")
    _require_string(contract.get("source_pin"), "source_pin")
    _require_string(contract.get("build_id"), "build_id")
    _require_equal(contract.get("actual_trace_derived"), True, "actual_trace_derived")
    _require_equal(contract.get("trace_collection_mode"), "redacted", "trace_collection_mode")
    _require_equal(contract.get("raw_secret_captured"), False, "raw_secret_captured")
    _require_equal(contract.get("public_safe"), True, "public_safe")
    _require_equal(contract.get("execution_allowed"), False, "execution_allowed")

    _validate_collector(_require_object(contract.get("collector"), "collector"))
    _validate_labels(_require_object(contract.get("labels"), "labels"))
    _validate_safety(_require_object(contract.get("safety"), "safety"))
    controls = set(_validate_string_list(contract.get("required_controls"), "required_controls"))
    missing_controls = sorted(REQUIRED_CONTROLS - controls)
    if missing_controls:
        raise OpenSSLTraceContractError(
            f"required_controls missing: {', '.join(missing_controls)}"
        )


def openssl_trace_contract_report_dict(contract: dict[str, Any]) -> dict[str, Any]:
    """Build a normalized OpenSSL trace collector contract report."""

    validate_openssl_trace_contract(contract)
    collector = contract["collector"]
    safety = contract["safety"]
    labels = contract["labels"]
    return {
        "report_type": "openssl_trace_contract_report",
        "status": "contract_ready_not_executed",
        "contract_id": contract["contract_id"],
        "target": contract["target"],
        "target_family": contract["target_family"],
        "target_version": contract["target_version"],
        "source_pin": contract["source_pin"],
        "build_id": contract["build_id"],
        "actual_trace_derived": contract["actual_trace_derived"],
        "trace_collection_mode": contract["trace_collection_mode"],
        "raw_secret_captured": contract["raw_secret_captured"],
        "public_safe": contract["public_safe"],
        "execution_allowed": contract["execution_allowed"],
        "produces_format": collector["produces_format"],
        "output_kind": collector["output_kind"],
        "required_record_fields": list(collector["required_record_fields"]),
        "allowed_value_channels": list(safety["allowed_value_channels"]),
        "disallowed_fields": list(safety["disallowed_fields"]),
        "lab_only_labels": labels["lab_only"],
        "allowed_label_keys": list(labels["allowed_label_keys"]),
        "required_controls": list(contract["required_controls"]),
        "notes": list(contract.get("notes", [])),
    }


def openssl_trace_contract_report_markdown(report: dict[str, Any]) -> str:
    """Render an OpenSSL trace collector contract report as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Trace Contract Report",
        "",
        f"- Contract: `{report['contract_id']}`",
        f"- Status: `{report['status']}`",
        f"- Target: `{report['target']}`",
        f"- Target family: `{report['target_family']}`",
        f"- Target version: `{report['target_version']}`",
        f"- Source pin: `{report['source_pin']}`",
        f"- Build ID: `{report['build_id']}`",
        f"- Actual trace derived: `{str(report['actual_trace_derived']).lower()}`",
        f"- Trace collection mode: `{report['trace_collection_mode']}`",
        f"- Raw secret captured: `{str(report['raw_secret_captured']).lower()}`",
        f"- Public safe: `{str(report['public_safe']).lower()}`",
        f"- Execution allowed by this validator: `{str(report['execution_allowed']).lower()}`",
        f"- Produces format: `{report['produces_format']}`",
        f"- Output kind: `{report['output_kind']}`",
        "",
        "## Required Record Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in report["required_record_fields"])
    lines.extend(["", "## Allowed Value Channels", ""])
    lines.extend(f"- `{channel}`" for channel in report["allowed_value_channels"])
    lines.extend(["", "## Disallowed Fields", ""])
    lines.extend(f"- `{field}`" for field in report["disallowed_fields"])
    lines.extend(["", "## Required Controls", ""])
    lines.extend(f"- `{control}`" for control in report["required_controls"])
    lines.extend(["", "## Label Contract", ""])
    lines.append(f"- Lab-only labels: `{str(report['lab_only_labels']).lower()}`")
    lines.extend(f"- Allowed label key: `{key}`" for key in report["allowed_label_keys"])

    notes = report.get("notes") or []
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
    lines.append("")
    return "\n".join(lines)


def write_openssl_trace_contract_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write an OpenSSL trace contract report as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_trace_contract_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write an OpenSSL trace contract report as Markdown."""

    Path(path).write_text(openssl_trace_contract_report_markdown(report), encoding="utf-8")


def _validate_collector(collector: dict[str, Any]) -> None:
    _require_string(collector.get("mode"), "collector.mode")
    _require_equal(collector.get("contract_only"), True, "collector.contract_only")
    _require_equal(collector.get("produces_format"), MODEL_SEQUENCE_FORMAT, "collector.produces_format")
    _require_equal(
        collector.get("output_kind"),
        "model_sequence_token_counts",
        "collector.output_kind",
    )
    fields = set(_validate_string_list(collector.get("required_record_fields"), "collector.required_record_fields"))
    missing = sorted(REQUIRED_RECORD_FIELDS - fields)
    if missing:
        raise OpenSSLTraceContractError(
            f"collector.required_record_fields missing: {', '.join(missing)}"
        )


def _validate_labels(labels: dict[str, Any]) -> None:
    _require_equal(labels.get("lab_only"), True, "labels.lab_only")
    _require_string(labels.get("label_source"), "labels.label_source")
    _validate_string_list(labels.get("allowed_label_keys"), "labels.allowed_label_keys", min_items=1)


def _validate_safety(safety: dict[str, Any]) -> None:
    _require_equal(safety.get("raw_trace_retention"), "forbidden", "safety.raw_trace_retention")
    disallowed = set(_validate_string_list(safety.get("disallowed_fields"), "safety.disallowed_fields"))
    missing = sorted(REQUIRED_DISALLOWED_FIELDS - disallowed)
    if missing:
        raise OpenSSLTraceContractError(f"safety.disallowed_fields missing: {', '.join(missing)}")
    channels = set(_validate_string_list(safety.get("allowed_value_channels"), "safety.allowed_value_channels"))
    missing_channels = sorted(REQUIRED_ALLOWED_VALUE_CHANNELS - channels)
    if missing_channels:
        raise OpenSSLTraceContractError(
            f"safety.allowed_value_channels missing: {', '.join(missing_channels)}"
        )
    forbidden_channels = sorted(channels & FORBIDDEN_ALLOWED_VALUE_CHANNELS)
    if forbidden_channels:
        raise OpenSSLTraceContractError(
            f"safety.allowed_value_channels must not include: {', '.join(forbidden_channels)}"
        )


def _require_openssl_target(value: str, name: str) -> None:
    if "openssl" not in value.lower():
        raise OpenSSLTraceContractError(f"{name} must identify an OpenSSL target")


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLTraceContractError(f"{name} must be an object")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    if not isinstance(value, list):
        raise OpenSSLTraceContractError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLTraceContractError(f"{name} must contain at least {min_items} item(s)")
    if not all(isinstance(item, str) and item for item in value):
        raise OpenSSLTraceContractError(f"{name} must contain only non-empty strings")
    return value


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLTraceContractError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLTraceContractError(f"{name} must be {expected!r}")
