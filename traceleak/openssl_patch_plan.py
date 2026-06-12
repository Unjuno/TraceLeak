"""Build a pre-application OpenSSL instrumentation patch plan.

A patch plan maps validated event-map groups to inspected source anchors. It does
not generate, apply, compile, or execute source patches.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_event_map import load_openssl_event_map
from traceleak.openssl_layout_inspection import inspect_openssl_layout_manifest

OPENSSL_PATCH_PLAN_FORMAT = "traceleak.openssl_patch_plan.v1"
ANCHOR_PREFERENCES = {
    "rsa_keygen_entry": [
        "RSA_generate_key_ex",
        "ossl_rsa_generate_multi_prime_key",
        "rsa_keygen",
    ],
    "prime_candidate_generation": [
        "probable_prime",
        "BN_generate_prime_ex2",
        "BN_generate_prime_ex",
    ],
    "prime_candidate_filter": [
        "probable_prime",
        "bn_is_prime_int",
    ],
    "probable_prime_test": [
        "bn_is_prime_int",
        "ossl_bn_check_prime",
    ],
    "prime_candidate_result": [
        "ossl_bn_check_generated_prime",
        "probable_prime",
        "bn_is_prime_int",
    ],
}


class OpenSSLPatchPlanError(ValueError):
    """Raised when a patch plan cannot be built or validated."""


def build_openssl_patch_plan(
    *,
    source_pin_path: str | Path,
    event_map_path: str | Path,
) -> dict[str, Any]:
    """Build an instrumentation patch plan from a pinned source manifest and event map."""

    event_map = load_openssl_event_map(event_map_path)
    inspection = inspect_openssl_layout_manifest(source_pin_path)
    _require_same_experiment(event_map, inspection)

    layout_by_group = _layout_by_group(inspection)
    planned_events = []
    for group in event_map["event_groups"]:
        planned_events.append(_planned_event(group=group, layout_by_group=layout_by_group))

    plan = {
        "format": OPENSSL_PATCH_PLAN_FORMAT,
        "report_type": "openssl_patch_plan",
        "status": "patch_plan_ready",
        "experiment_id": event_map["experiment_id"],
        "target_family": event_map["target_family"],
        "exact_commit_sha": inspection["exact_commit_sha"],
        "worktree_path": inspection["worktree_path"],
        "dirty": inspection["dirty"],
        "execution_allowed": False,
        "patch_application_allowed": False,
        "trace_view": event_map["trace_view"],
        "raw_secret_capture_allowed": event_map["raw_secret_capture_allowed"],
        "planned_events": planned_events,
        "gates": [
            "source_pin_validated",
            "event_map_validated",
            "layout_inspected",
            "manual_patch_review_required",
            "no_raw_secret_capture",
            "redacted_values_only",
        ],
        "notes": [
            "This is a review artifact only; it does not generate or apply a patch.",
            "Anchor lines must be rechecked immediately before any patch is written.",
            "Insertion policies are conservative and require manual review.",
        ],
    }
    validate_openssl_patch_plan(plan)
    return plan


def validate_openssl_patch_plan(plan: dict[str, Any]) -> None:
    """Validate a generated OpenSSL patch plan."""

    _require_equal(plan.get("format"), OPENSSL_PATCH_PLAN_FORMAT, "format")
    _require_equal(plan.get("report_type"), "openssl_patch_plan", "report_type")
    _require_equal(plan.get("status"), "patch_plan_ready", "status")
    _require_equal(plan.get("execution_allowed"), False, "execution_allowed")
    _require_equal(plan.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(plan.get("trace_view"), "redacted", "trace_view")
    _require_equal(plan.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_string(plan.get("experiment_id"), "experiment_id")
    _require_string(plan.get("exact_commit_sha"), "exact_commit_sha")
    planned_events = _require_list(plan.get("planned_events"), "planned_events", min_items=1)
    seen_group_ids: set[str] = set()
    for index, event in enumerate(planned_events):
        _validate_planned_event(event, index=index, seen_group_ids=seen_group_ids)


def patch_plan_markdown(plan: dict[str, Any]) -> str:
    """Render a patch plan as Markdown."""

    validate_openssl_patch_plan(plan)
    lines = [
        "# TraceLeak OpenSSL Instrumentation Patch Plan",
        "",
        f"- Experiment: `{plan['experiment_id']}`",
        f"- Target family: `{plan['target_family']}`",
        f"- Commit: `{plan['exact_commit_sha']}`",
        f"- Worktree: `{plan['worktree_path']}`",
        f"- Dirty: `{str(plan['dirty']).lower()}`",
        f"- Execution allowed: `{str(plan['execution_allowed']).lower()}`",
        f"- Patch application allowed: `{str(plan['patch_application_allowed']).lower()}`",
        "",
        "## Planned Events",
        "",
        "| Event group | Path | Anchor symbol | Anchor line | Policy | Redacted values |",
        "|---|---|---|---:|---|---|",
    ]
    for event in plan["planned_events"]:
        lines.append(
            "| `{group}` | `{path}` | `{symbol}` | `{line}` | `{policy}` | `{values}` |".format(
                group=event["group_id"],
                path=event["target_path"],
                symbol=event["anchor_symbol"],
                line=event["anchor_line"],
                policy=event["insertion_policy"],
                values=", ".join(event["redacted_values"]),
            )
        )
    lines.extend(["", "## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in plan["gates"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in plan.get("notes", []))
    lines.append("")
    return "\n".join(lines)


def write_patch_plan_json(path: str | Path, plan: dict[str, Any]) -> None:
    """Write patch plan JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_patch_plan_markdown(path: str | Path, plan: dict[str, Any]) -> None:
    """Write patch plan Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(patch_plan_markdown(plan), encoding="utf-8")


def _require_same_experiment(event_map: dict[str, Any], inspection: dict[str, Any]) -> None:
    for field in ("experiment_id", "target_family"):
        if event_map.get(field) != inspection.get(field):
            raise OpenSSLPatchPlanError(f"{field} mismatch between event map and layout inspection")


def _layout_by_group(inspection: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in inspection["layout"]:
        for group_id in item["related_event_groups"]:
            if group_id in result:
                raise OpenSSLPatchPlanError(f"duplicate layout coverage for event group: {group_id}")
            result[group_id] = item
    return result


def _planned_event(*, group: dict[str, Any], layout_by_group: dict[str, dict[str, Any]]) -> dict[str, Any]:
    group_id = group["group_id"]
    if group_id not in layout_by_group:
        raise OpenSSLPatchPlanError(f"event group is not covered by layout inspection: {group_id}")
    layout = layout_by_group[group_id]
    if group["target_path"] != layout["target_path"]:
        raise OpenSSLPatchPlanError(f"target_path mismatch for event group: {group_id}")
    anchor = _choose_anchor(group_id=group_id, symbols=layout["symbols"])
    return {
        "group_id": group_id,
        "target_path": group["target_path"],
        "phase": group["phase"],
        "event_type": group["event_type"],
        "event_name": group["name"],
        "anchor_symbol": anchor["name"],
        "anchor_line": anchor["first_line"],
        "all_anchor_lines": list(anchor["line_numbers"]),
        "insertion_policy": _insertion_policy(group["event_type"]),
        "capture_fields": list(group["capture"]),
        "redacted_values": list(group["redacted_values"]),
        "forbidden_values": list(group["forbidden_values"]),
        "manual_review_required": True,
    }


def _choose_anchor(*, group_id: str, symbols: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {symbol["name"]: symbol for symbol in symbols}
    for name in ANCHOR_PREFERENCES.get(group_id, []):
        if name in by_name:
            return by_name[name]
    return symbols[0]


def _insertion_policy(event_type: str) -> str:
    if event_type == "phase":
        return "near_anchor_function_entry_after_validation"
    if event_type == "loop":
        return "inside_existing_loop_manual_review"
    if event_type == "branch":
        return "near_result_branch_manual_review"
    return "manual_review_required"


def _validate_planned_event(event: Any, *, index: int, seen_group_ids: set[str]) -> None:
    if not isinstance(event, dict):
        raise OpenSSLPatchPlanError(f"planned_events[{index}] must be an object")
    group_id = _require_string(event.get("group_id"), f"planned_events[{index}].group_id")
    if group_id in seen_group_ids:
        raise OpenSSLPatchPlanError(f"duplicate planned event group_id: {group_id}")
    seen_group_ids.add(group_id)
    _require_string(event.get("target_path"), f"planned_events[{index}].target_path")
    _require_string(event.get("anchor_symbol"), f"planned_events[{index}].anchor_symbol")
    anchor_line = event.get("anchor_line")
    if not isinstance(anchor_line, int) or anchor_line <= 0:
        raise OpenSSLPatchPlanError(f"planned_events[{index}].anchor_line must be a positive integer")
    _require_equal(event.get("manual_review_required"), True, f"planned_events[{index}].manual_review_required")
    _require_list(event.get("capture_fields"), f"planned_events[{index}].capture_fields", min_items=1)
    redacted_values = _require_list(
        event.get("redacted_values"),
        f"planned_events[{index}].redacted_values",
        min_items=1,
    )
    forbidden_values = set(
        _require_list(event.get("forbidden_values"), f"planned_events[{index}].forbidden_values", min_items=1)
    )
    overlap = sorted(set(redacted_values) & forbidden_values)
    if overlap:
        raise OpenSSLPatchPlanError(
            f"planned_events[{index}].redacted_values overlap forbidden_values: {', '.join(overlap)}"
        )


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLPatchPlanError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLPatchPlanError(f"{name} must contain at least {min_items} item(s)")
    return value


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLPatchPlanError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLPatchPlanError(f"{name} must be {expected!r}")
