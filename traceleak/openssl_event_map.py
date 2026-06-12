"""OpenSSL event-map validation and reporting.

An event map is a pre-instrumentation contract. It fixes which redacted events
are intended to be collected before any OpenSSL execution or patching begins.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OPENSSL_EVENT_MAP_FORMAT = "traceleak.openssl_event_map.v1"
ALLOWED_EVENT_TYPES = {"phase", "loop", "branch", "counter"}
REQUIRED_EVENT_FIELDS = {"function", "file", "line", "phase", "event_type", "name"}
REQUIRED_GATES = {
    "source_ref_pinned",
    "redacted_view_only",
    "no_raw_secret_fields",
    "label_overlap_features_blocked",
    "strict_label_audit_required",
    "ablation_validation_required",
    "negative_controls_required",
}
REQUIRED_CONTROLS = {
    "shuffled_label_negative_control",
    "public_only_baseline",
    "seed_relabel_control",
}
FORBIDDEN_RAW_VALUE_NAMES = {
    "p",
    "q",
    "d",
    "dp",
    "dq",
    "iqmp",
    "private_key",
    "raw_bignum",
    "prime_candidate",
    "candidate_value",
    "seed",
    "rng_state",
}


class OpenSSLEventMapError(ValueError):
    """Raised when an OpenSSL event map is invalid."""


def load_openssl_event_map(path: str | Path) -> dict[str, Any]:
    """Load and validate an OpenSSL event map."""

    input_path = Path(path)
    if not input_path.exists():
        raise OpenSSLEventMapError(f"event map not found: {input_path}")
    try:
        event_map = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OpenSSLEventMapError(f"invalid JSON in {input_path}: {exc}") from exc
    if not isinstance(event_map, dict):
        raise OpenSSLEventMapError("event map must be a JSON object")
    validate_openssl_event_map(event_map)
    return event_map


def validate_openssl_event_map(event_map: dict[str, Any]) -> None:
    """Validate an OpenSSL event-map contract."""

    _require_equal(event_map.get("format"), OPENSSL_EVENT_MAP_FORMAT, "format")
    _require_string(event_map.get("experiment_id"), "experiment_id")
    target_family = _require_string(event_map.get("target_family"), "target_family")
    if "openssl" not in target_family.lower():
        raise OpenSSLEventMapError("target_family must identify an OpenSSL target")
    _require_equal(event_map.get("source_ref_policy"), "pin_exact_commit_before_run", "source_ref_policy")
    _require_equal(event_map.get("execution_allowed"), False, "execution_allowed")
    _require_equal(event_map.get("public_safe"), True, "public_safe")
    _require_equal(event_map.get("trace_view"), "redacted", "trace_view")
    _require_equal(event_map.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _validate_label_policy(_require_object(event_map.get("label_policy"), "label_policy"))

    groups = _require_list(event_map.get("event_groups"), "event_groups", min_items=1)
    seen_group_ids: set[str] = set()
    for index, group in enumerate(groups):
        _validate_event_group(group, index=index, seen_group_ids=seen_group_ids)

    controls = set(_validate_string_list(event_map.get("required_controls"), "required_controls", min_items=1))
    missing_controls = sorted(REQUIRED_CONTROLS - controls)
    if missing_controls:
        raise OpenSSLEventMapError(f"required_controls missing: {', '.join(missing_controls)}")

    gates = set(_validate_string_list(event_map.get("gates"), "gates", min_items=len(REQUIRED_GATES)))
    missing_gates = sorted(REQUIRED_GATES - gates)
    if missing_gates:
        raise OpenSSLEventMapError(f"gates missing: {', '.join(missing_gates)}")


def openssl_event_map_report_dict(event_map: dict[str, Any]) -> dict[str, Any]:
    """Build a normalized event-map report."""

    validate_openssl_event_map(event_map)
    groups = event_map["event_groups"]
    return {
        "report_type": "openssl_event_map_report",
        "status": "event_map_ready",
        "experiment_id": event_map["experiment_id"],
        "target_family": event_map["target_family"],
        "execution_allowed": event_map["execution_allowed"],
        "trace_view": event_map["trace_view"],
        "group_count": len(groups),
        "target_paths": sorted({group["target_path"] for group in groups}),
        "event_types": sorted({group["event_type"] for group in groups}),
        "phases": sorted({group["phase"] for group in groups}),
        "groups": [
            {
                "group_id": group["group_id"],
                "target_path": group["target_path"],
                "phase": group["phase"],
                "event_type": group["event_type"],
                "name": group["name"],
                "redacted_values": list(group.get("redacted_values", [])),
            }
            for group in groups
        ],
        "gates": list(event_map["gates"]),
        "required_controls": list(event_map["required_controls"]),
        "notes": list(event_map.get("notes", [])),
    }


def openssl_event_map_report_markdown(report: dict[str, Any]) -> str:
    """Render an OpenSSL event-map report as Markdown."""

    lines = [
        "# TraceLeak OpenSSL Event Map Report",
        "",
        f"- Experiment: `{report['experiment_id']}`",
        f"- Target family: `{report['target_family']}`",
        f"- Status: `{report['status']}`",
        f"- Execution allowed: `{str(report['execution_allowed']).lower()}`",
        f"- Trace view: `{report['trace_view']}`",
        f"- Event groups: `{report['group_count']}`",
        "",
        "## Event Groups",
        "",
        "| Group | Path | Phase | Type | Redacted values |",
        "|---|---|---|---|---|",
    ]
    for group in report["groups"]:
        lines.append(
            "| `{group_id}` | `{target_path}` | `{phase}` | `{event_type}` | `{values}` |".format(
                group_id=group["group_id"],
                target_path=group["target_path"],
                phase=group["phase"],
                event_type=group["event_type"],
                values=", ".join(group["redacted_values"]),
            )
        )
    lines.extend(["", "## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in report["gates"])
    lines.extend(["", "## Required Controls", ""])
    lines.extend(f"- `{control}`" for control in report["required_controls"])
    notes = report.get("notes") or []
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
    lines.append("")
    return "\n".join(lines)


def write_openssl_event_map_report_json(path: str | Path, report: dict[str, Any]) -> None:
    """Write an OpenSSL event-map report as JSON."""

    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_openssl_event_map_report_markdown(path: str | Path, report: dict[str, Any]) -> None:
    """Write an OpenSSL event-map report as Markdown."""

    Path(path).write_text(openssl_event_map_report_markdown(report), encoding="utf-8")


def _validate_label_policy(label_policy: dict[str, Any]) -> None:
    _require_equal(label_policy.get("lab_only"), True, "label_policy.lab_only")
    forbidden_public = set(
        _validate_string_list(
            label_policy.get("forbidden_public_label_fields"),
            "label_policy.forbidden_public_label_fields",
            min_items=1,
        )
    )
    missing_forbidden = sorted({"p", "q", "d", "private_key", "seed"} - forbidden_public)
    if missing_forbidden:
        raise OpenSSLEventMapError(
            f"label_policy.forbidden_public_label_fields missing: {', '.join(missing_forbidden)}"
        )
    _validate_string_list(label_policy.get("planned_label_keys"), "label_policy.planned_label_keys", min_items=1)


def _validate_event_group(group: Any, *, index: int, seen_group_ids: set[str]) -> None:
    if not isinstance(group, dict):
        raise OpenSSLEventMapError(f"event_groups[{index}] must be an object")
    group_id = _require_string(group.get("group_id"), f"event_groups[{index}].group_id")
    if group_id in seen_group_ids:
        raise OpenSSLEventMapError(f"duplicate event group_id: {group_id}")
    seen_group_ids.add(group_id)
    target_path = _require_string(group.get("target_path"), f"event_groups[{index}].target_path")
    if not target_path.endswith(".c"):
        raise OpenSSLEventMapError(f"event_groups[{index}].target_path must be a C source file")
    _require_string(group.get("phase"), f"event_groups[{index}].phase")
    event_type = _require_string(group.get("event_type"), f"event_groups[{index}].event_type")
    if event_type not in ALLOWED_EVENT_TYPES:
        raise OpenSSLEventMapError(f"event_groups[{index}].event_type is not allowed: {event_type}")
    _require_string(group.get("name"), f"event_groups[{index}].name")
    capture = set(_validate_string_list(group.get("capture"), f"event_groups[{index}].capture", min_items=1))
    missing_capture = sorted(REQUIRED_EVENT_FIELDS - capture)
    if missing_capture:
        raise OpenSSLEventMapError(
            f"event_groups[{index}].capture missing: {', '.join(missing_capture)}"
        )
    redacted_values = _validate_string_list(
        group.get("redacted_values"),
        f"event_groups[{index}].redacted_values",
        min_items=1,
    )
    forbidden_values = set(
        _validate_string_list(group.get("forbidden_values"), f"event_groups[{index}].forbidden_values", min_items=1)
    )
    raw_overlap = sorted(FORBIDDEN_RAW_VALUE_NAMES & set(redacted_values))
    if raw_overlap:
        raise OpenSSLEventMapError(
            f"event_groups[{index}].redacted_values include forbidden raw names: {', '.join(raw_overlap)}"
        )
    missing_common = sorted((FORBIDDEN_RAW_VALUE_NAMES & {"private_key", "raw_bignum"}) - forbidden_values)
    if missing_common:
        raise OpenSSLEventMapError(
            f"event_groups[{index}].forbidden_values missing: {', '.join(missing_common)}"
        )


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OpenSSLEventMapError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLEventMapError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLEventMapError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLEventMapError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLEventMapError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLEventMapError(f"{name} must be {expected!r}")
