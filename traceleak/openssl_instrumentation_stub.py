"""Build a review-only OpenSSL instrumentation stub specification.

The stub specification defines allowed event payload fields and redaction rules.
It does not generate source edits, modify OpenSSL, compile OpenSSL, or execute
OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_patch_plan import build_openssl_patch_plan

OPENSSL_INSTRUMENTATION_STUB_FORMAT = "traceleak.openssl_instrumentation_stub.v1"
REQUIRED_PAYLOAD_FIELDS = [
    "step",
    "phase",
    "function",
    "file",
    "line",
    "event_type",
    "name",
    "value_redacted",
]
REQUIRED_GATES = [
    "source_pin_validated",
    "event_map_validated",
    "layout_inspected",
    "patch_plan_reviewed",
    "manual_stub_review_required",
    "redacted_payload_only",
    "no_raw_secret_capture",
]


class OpenSSLInstrumentationStubError(ValueError):
    """Raised when an instrumentation stub specification is invalid."""


def build_openssl_instrumentation_stub(
    *,
    source_pin_path: str | Path,
    event_map_path: str | Path,
) -> dict[str, Any]:
    """Build a review-only instrumentation stub specification."""

    patch_plan = build_openssl_patch_plan(
        source_pin_path=source_pin_path,
        event_map_path=event_map_path,
    )
    forbidden_values = sorted(
        {
            value
            for event in patch_plan["planned_events"]
            for value in event.get("forbidden_values", [])
        }
    )
    redacted_values = sorted(
        {
            value
            for event in patch_plan["planned_events"]
            for value in event.get("redacted_values", [])
        }
    )
    stub = {
        "format": OPENSSL_INSTRUMENTATION_STUB_FORMAT,
        "report_type": "openssl_instrumentation_stub",
        "status": "stub_spec_ready",
        "experiment_id": patch_plan["experiment_id"],
        "target_family": patch_plan["target_family"],
        "exact_commit_sha": patch_plan["exact_commit_sha"],
        "worktree_path": patch_plan["worktree_path"],
        "dirty": patch_plan["dirty"],
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "compile_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_view": "redacted",
        "stub_api": {
            "name": "traceleak_event",
            "kind": "review_only_event_payload_contract",
            "required_payload_fields": list(REQUIRED_PAYLOAD_FIELDS),
            "value_field": "value_redacted",
            "raw_value_field_allowed": False,
        },
        "redaction_policy": {
            "allowed_value_names": redacted_values,
            "forbidden_value_names": forbidden_values,
            "only_bucketed_values_allowed": True,
            "raw_bignum_allowed": False,
            "private_key_material_allowed": False,
        },
        "planned_events": [
            {
                "group_id": event["group_id"],
                "target_path": event["target_path"],
                "anchor_symbol": event["anchor_symbol"],
                "anchor_line": event["anchor_line"],
                "event_type": event["event_type"],
                "payload_fields": list(REQUIRED_PAYLOAD_FIELDS),
                "redacted_values": list(event["redacted_values"]),
                "manual_review_required": True,
            }
            for event in patch_plan["planned_events"]
        ],
        "gates": list(REQUIRED_GATES),
        "notes": [
            "This is a review-only event payload contract.",
            "It does not create source changes or execute OpenSSL.",
            "Only value_redacted bucket names are allowed as event values.",
            "Any later source edit must be reviewed against this contract and the pinned commit.",
        ],
    }
    validate_openssl_instrumentation_stub(stub)
    return stub


def validate_openssl_instrumentation_stub(stub: dict[str, Any]) -> None:
    """Validate an OpenSSL instrumentation stub specification."""

    _require_equal(stub.get("format"), OPENSSL_INSTRUMENTATION_STUB_FORMAT, "format")
    _require_equal(stub.get("report_type"), "openssl_instrumentation_stub", "report_type")
    _require_equal(stub.get("status"), "stub_spec_ready", "status")
    _require_equal(stub.get("execution_allowed"), False, "execution_allowed")
    _require_equal(stub.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(stub.get("compile_allowed"), False, "compile_allowed")
    _require_equal(stub.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(stub.get("trace_view"), "redacted", "trace_view")
    _require_string(stub.get("experiment_id"), "experiment_id")
    _require_string(stub.get("exact_commit_sha"), "exact_commit_sha")
    _validate_stub_api(_require_object(stub.get("stub_api"), "stub_api"))
    _validate_redaction_policy(_require_object(stub.get("redaction_policy"), "redaction_policy"))
    planned_events = _require_list(stub.get("planned_events"), "planned_events", min_items=1)
    for index, event in enumerate(planned_events):
        _validate_planned_event(event, index=index)
    gates = set(_validate_string_list(stub.get("gates"), "gates", min_items=len(REQUIRED_GATES)))
    missing_gates = sorted(set(REQUIRED_GATES) - gates)
    if missing_gates:
        raise OpenSSLInstrumentationStubError(f"gates missing: {', '.join(missing_gates)}")


def instrumentation_stub_markdown(stub: dict[str, Any]) -> str:
    """Render an instrumentation stub specification as Markdown."""

    validate_openssl_instrumentation_stub(stub)
    lines = [
        "# TraceLeak OpenSSL Instrumentation Stub Spec",
        "",
        f"- Experiment: `{stub['experiment_id']}`",
        f"- Target family: `{stub['target_family']}`",
        f"- Commit: `{stub['exact_commit_sha']}`",
        f"- Worktree: `{stub['worktree_path']}`",
        f"- Dirty: `{str(stub['dirty']).lower()}`",
        f"- Execution allowed: `{str(stub['execution_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(stub['source_mutation_allowed']).lower()}`",
        f"- Compile allowed: `{str(stub['compile_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(stub['raw_secret_capture_allowed']).lower()}`",
        "",
        "## Stub API",
        "",
        f"- Name: `{stub['stub_api']['name']}`",
        f"- Value field: `{stub['stub_api']['value_field']}`",
        f"- Raw value field allowed: `{str(stub['stub_api']['raw_value_field_allowed']).lower()}`",
        "",
        "## Required Payload Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in stub["stub_api"]["required_payload_fields"])
    lines.extend(
        [
            "",
            "## Planned Event Payloads",
            "",
            "| Event group | Path | Anchor symbol | Anchor line | Redacted values |",
            "|---|---|---|---:|---|",
        ]
    )
    for event in stub["planned_events"]:
        lines.append(
            "| `{group}` | `{path}` | `{symbol}` | `{line}` | `{values}` |".format(
                group=event["group_id"],
                path=event["target_path"],
                symbol=event["anchor_symbol"],
                line=event["anchor_line"],
                values=", ".join(event["redacted_values"]),
            )
        )
    lines.extend(["", "## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in stub["gates"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in stub.get("notes", []))
    lines.append("")
    return "\n".join(lines)


def write_instrumentation_stub_json(path: str | Path, stub: dict[str, Any]) -> None:
    """Write instrumentation stub specification JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(stub, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_instrumentation_stub_markdown(path: str | Path, stub: dict[str, Any]) -> None:
    """Write instrumentation stub specification Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(instrumentation_stub_markdown(stub), encoding="utf-8")


def _validate_stub_api(stub_api: dict[str, Any]) -> None:
    _require_equal(stub_api.get("name"), "traceleak_event", "stub_api.name")
    _require_equal(stub_api.get("value_field"), "value_redacted", "stub_api.value_field")
    _require_equal(stub_api.get("raw_value_field_allowed"), False, "stub_api.raw_value_field_allowed")
    fields = _validate_string_list(
        stub_api.get("required_payload_fields"),
        "stub_api.required_payload_fields",
        min_items=len(REQUIRED_PAYLOAD_FIELDS),
    )
    missing = sorted(set(REQUIRED_PAYLOAD_FIELDS) - set(fields))
    if missing:
        raise OpenSSLInstrumentationStubError(
            f"stub_api.required_payload_fields missing: {', '.join(missing)}"
        )


def _validate_redaction_policy(policy: dict[str, Any]) -> None:
    _require_equal(policy.get("only_bucketed_values_allowed"), True, "redaction_policy.only_bucketed_values_allowed")
    _require_equal(policy.get("raw_bignum_allowed"), False, "redaction_policy.raw_bignum_allowed")
    _require_equal(
        policy.get("private_key_material_allowed"),
        False,
        "redaction_policy.private_key_material_allowed",
    )
    _validate_string_list(policy.get("allowed_value_names"), "redaction_policy.allowed_value_names", min_items=1)
    forbidden = set(
        _validate_string_list(
            policy.get("forbidden_value_names"),
            "redaction_policy.forbidden_value_names",
            min_items=1,
        )
    )
    allowed = set(policy["allowed_value_names"])
    overlap = sorted(allowed & forbidden)
    if overlap:
        raise OpenSSLInstrumentationStubError(
            f"redaction_policy.allowed_value_names overlap forbidden_value_names: {', '.join(overlap)}"
        )


def _validate_planned_event(event: Any, *, index: int) -> None:
    if not isinstance(event, dict):
        raise OpenSSLInstrumentationStubError(f"planned_events[{index}] must be an object")
    _require_string(event.get("group_id"), f"planned_events[{index}].group_id")
    _require_string(event.get("target_path"), f"planned_events[{index}].target_path")
    _require_string(event.get("anchor_symbol"), f"planned_events[{index}].anchor_symbol")
    anchor_line = event.get("anchor_line")
    if not isinstance(anchor_line, int) or anchor_line <= 0:
        raise OpenSSLInstrumentationStubError(
            f"planned_events[{index}].anchor_line must be a positive integer"
        )
    _require_equal(event.get("manual_review_required"), True, f"planned_events[{index}].manual_review_required")
    fields = set(
        _validate_string_list(
            event.get("payload_fields"),
            f"planned_events[{index}].payload_fields",
            min_items=len(REQUIRED_PAYLOAD_FIELDS),
        )
    )
    missing = sorted(set(REQUIRED_PAYLOAD_FIELDS) - fields)
    if missing:
        raise OpenSSLInstrumentationStubError(
            f"planned_events[{index}].payload_fields missing: {', '.join(missing)}"
        )
    _validate_string_list(event.get("redacted_values"), f"planned_events[{index}].redacted_values", min_items=1)


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLInstrumentationStubError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLInstrumentationStubError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLInstrumentationStubError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLInstrumentationStubError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLInstrumentationStubError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLInstrumentationStubError(f"{name} must be {expected!r}")
