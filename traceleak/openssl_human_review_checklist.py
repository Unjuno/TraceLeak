"""Build a human-review checklist for OpenSSL event slots.

The checklist is a review scaffold only. It does not approve event slots, generate
source text, generate diffs, modify OpenSSL, compile OpenSSL, or execute OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_source_edit_proposal import build_openssl_source_edit_proposal

OPENSSL_HUMAN_REVIEW_CHECKLIST_FORMAT = "traceleak.openssl_human_review_checklist.v1"
REQUIRED_CHECK_IDS = [
    "pinned_commit_matches",
    "anchor_still_matches",
    "payload_fields_match_stub",
    "value_redacted_only",
    "no_raw_secret_material",
    "placement_policy_reviewed",
    "experiment_need_justified",
]
REQUIRED_GATES = [
    "source_pin_validated",
    "event_map_validated",
    "layout_inspected",
    "patch_plan_reviewed",
    "stub_spec_reviewed",
    "event_slot_reviewed",
    "human_review_required",
    "no_source_text_generated",
    "no_raw_secret_capture",
]


class OpenSSLHumanReviewChecklistError(ValueError):
    """Raised when a human-review checklist is invalid."""


def build_openssl_human_review_checklist(
    *,
    source_pin_path: str | Path,
    event_map_path: str | Path,
) -> dict[str, Any]:
    """Build a human-review checklist for planned OpenSSL event slots."""

    proposal = build_openssl_source_edit_proposal(
        source_pin_path=source_pin_path,
        event_map_path=event_map_path,
    )
    items = []
    for slot in proposal["proposals"]:
        items.append(
            {
                "proposal_id": slot["proposal_id"],
                "group_id": slot["group_id"],
                "target_path": slot["target_path"],
                "anchor_symbol": slot["anchor_symbol"],
                "anchor_line": slot["anchor_line"],
                "placement_policy": slot["placement_policy"],
                "review_status": "unchecked",
                "checks": _checks_for_slot(),
            }
        )
    checklist = {
        "format": OPENSSL_HUMAN_REVIEW_CHECKLIST_FORMAT,
        "report_type": "openssl_human_review_checklist",
        "status": "review_checklist_ready",
        "experiment_id": proposal["experiment_id"],
        "target_family": proposal["target_family"],
        "exact_commit_sha": proposal["exact_commit_sha"],
        "worktree_path": proposal["worktree_path"],
        "dirty": proposal["dirty"],
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "compile_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "raw_secret_capture_allowed": False,
        "approval_recorded": False,
        "trace_view": "redacted",
        "review_items": items,
        "gates": list(REQUIRED_GATES),
        "notes": [
            "This artifact is a checklist only and records no approval.",
            "All review items start as unchecked.",
            "A later approval artifact must be separate from this checklist.",
        ],
    }
    validate_openssl_human_review_checklist(checklist)
    return checklist


def validate_openssl_human_review_checklist(checklist: dict[str, Any]) -> None:
    """Validate a human-review checklist artifact."""

    _require_equal(checklist.get("format"), OPENSSL_HUMAN_REVIEW_CHECKLIST_FORMAT, "format")
    _require_equal(checklist.get("report_type"), "openssl_human_review_checklist", "report_type")
    _require_equal(checklist.get("status"), "review_checklist_ready", "status")
    _require_equal(checklist.get("execution_allowed"), False, "execution_allowed")
    _require_equal(checklist.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(checklist.get("compile_allowed"), False, "compile_allowed")
    _require_equal(checklist.get("diff_generation_allowed"), False, "diff_generation_allowed")
    _require_equal(checklist.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(checklist.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(checklist.get("approval_recorded"), False, "approval_recorded")
    _require_string(checklist.get("experiment_id"), "experiment_id")
    _require_string(checklist.get("exact_commit_sha"), "exact_commit_sha")
    items = _require_list(checklist.get("review_items"), "review_items", min_items=1)
    for index, item in enumerate(items):
        _validate_review_item(item, index=index)
    gates = set(_validate_string_list(checklist.get("gates"), "gates", min_items=len(REQUIRED_GATES)))
    missing_gates = sorted(set(REQUIRED_GATES) - gates)
    if missing_gates:
        raise OpenSSLHumanReviewChecklistError(f"gates missing: {', '.join(missing_gates)}")


def human_review_checklist_markdown(checklist: dict[str, Any]) -> str:
    """Render a human-review checklist as Markdown."""

    validate_openssl_human_review_checklist(checklist)
    lines = [
        "# TraceLeak OpenSSL Human Review Checklist",
        "",
        f"- Experiment: `{checklist['experiment_id']}`",
        f"- Target family: `{checklist['target_family']}`",
        f"- Commit: `{checklist['exact_commit_sha']}`",
        f"- Worktree: `{checklist['worktree_path']}`",
        f"- Dirty: `{str(checklist['dirty']).lower()}`",
        f"- Execution allowed: `{str(checklist['execution_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(checklist['source_mutation_allowed']).lower()}`",
        f"- Diff generation allowed: `{str(checklist['diff_generation_allowed']).lower()}`",
        f"- Patch application allowed: `{str(checklist['patch_application_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(checklist['raw_secret_capture_allowed']).lower()}`",
        f"- Approval recorded: `{str(checklist['approval_recorded']).lower()}`",
        "",
        "## Review Items",
        "",
    ]
    for item in checklist["review_items"]:
        lines.extend(
            [
                f"### `{item['proposal_id']}` / `{item['group_id']}`",
                "",
                f"- Path: `{item['target_path']}`",
                f"- Anchor: `{item['anchor_symbol']}` line `{item['anchor_line']}`",
                f"- Placement policy: `{item['placement_policy']}`",
                f"- Review status: `{item['review_status']}`",
                "",
            ]
        )
        lines.extend(f"- [ ] `{check['check_id']}` — {check['question']}" for check in item["checks"])
        lines.append("")
    lines.extend(["## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in checklist["gates"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in checklist.get("notes", []))
    lines.append("")
    return "\n".join(lines)


def write_human_review_checklist_json(path: str | Path, checklist: dict[str, Any]) -> None:
    """Write human-review checklist JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(checklist, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_human_review_checklist_markdown(path: str | Path, checklist: dict[str, Any]) -> None:
    """Write human-review checklist Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(human_review_checklist_markdown(checklist), encoding="utf-8")


def _checks_for_slot() -> list[dict[str, str]]:
    return [
        {
            "check_id": "pinned_commit_matches",
            "question": "Confirm the pinned commit matches the inspected worktree.",
        },
        {
            "check_id": "anchor_still_matches",
            "question": "Confirm the anchor symbol and line still identify the intended source location.",
        },
        {
            "check_id": "payload_fields_match_stub",
            "question": "Confirm the event payload fields match the stub specification.",
        },
        {
            "check_id": "value_redacted_only",
            "question": "Confirm the event uses value_redacted bucket names only.",
        },
        {
            "check_id": "no_raw_secret_material",
            "question": "Confirm the event would not expose raw private-key or bignum material.",
        },
        {
            "check_id": "placement_policy_reviewed",
            "question": "Confirm the placement policy is appropriate for the event type.",
        },
        {
            "check_id": "experiment_need_justified",
            "question": "Confirm the event is necessary for the planned leakage experiment.",
        },
    ]


def _validate_review_item(item: Any, *, index: int) -> None:
    if not isinstance(item, dict):
        raise OpenSSLHumanReviewChecklistError(f"review_items[{index}] must be an object")
    _require_string(item.get("proposal_id"), f"review_items[{index}].proposal_id")
    _require_string(item.get("group_id"), f"review_items[{index}].group_id")
    _require_string(item.get("target_path"), f"review_items[{index}].target_path")
    _require_string(item.get("anchor_symbol"), f"review_items[{index}].anchor_symbol")
    anchor_line = item.get("anchor_line")
    if not isinstance(anchor_line, int) or anchor_line <= 0:
        raise OpenSSLHumanReviewChecklistError(
            f"review_items[{index}].anchor_line must be a positive integer"
        )
    _require_equal(item.get("review_status"), "unchecked", f"review_items[{index}].review_status")
    checks = _require_list(item.get("checks"), f"review_items[{index}].checks", min_items=len(REQUIRED_CHECK_IDS))
    check_ids = {check.get("check_id") for check in checks if isinstance(check, dict)}
    missing = sorted(set(REQUIRED_CHECK_IDS) - check_ids)
    if missing:
        raise OpenSSLHumanReviewChecklistError(
            f"review_items[{index}].checks missing: {', '.join(missing)}"
        )


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLHumanReviewChecklistError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLHumanReviewChecklistError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLHumanReviewChecklistError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLHumanReviewChecklistError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLHumanReviewChecklistError(f"{name} must be {expected!r}")
