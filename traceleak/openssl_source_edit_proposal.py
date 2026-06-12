"""Build a review-only OpenSSL source edit proposal.

The proposal maps approved event payload contracts to source anchor slots. It does
not generate diffs, write source text, modify OpenSSL, compile OpenSSL, or execute
OpenSSL.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.openssl_instrumentation_stub import build_openssl_instrumentation_stub

OPENSSL_SOURCE_EDIT_PROPOSAL_FORMAT = "traceleak.openssl_source_edit_proposal.v1"
DISALLOWED_PROPOSAL_KEYS = {
    "diff",
    "patch",
    "source_text",
    "insert_text",
    "replacement_text",
}
REQUIRED_GATES = [
    "source_pin_validated",
    "event_map_validated",
    "layout_inspected",
    "patch_plan_reviewed",
    "stub_spec_reviewed",
    "source_edit_proposal_review_required",
    "no_source_text_generated",
    "no_raw_secret_capture",
]


class OpenSSLSourceEditProposalError(ValueError):
    """Raised when a source edit proposal is invalid."""


def build_openssl_source_edit_proposal(
    *,
    source_pin_path: str | Path,
    event_map_path: str | Path,
) -> dict[str, Any]:
    """Build a review-only OpenSSL source edit proposal."""

    stub = build_openssl_instrumentation_stub(
        source_pin_path=source_pin_path,
        event_map_path=event_map_path,
    )
    proposals = []
    for index, event in enumerate(stub["planned_events"], start=1):
        proposals.append(
            {
                "proposal_id": f"openssl_edit_slot_{index:03d}",
                "group_id": event["group_id"],
                "target_path": event["target_path"],
                "anchor_symbol": event["anchor_symbol"],
                "anchor_line": event["anchor_line"],
                "placement_policy": _placement_policy(event["event_type"]),
                "stub_api_name": stub["stub_api"]["name"],
                "payload_fields": list(event["payload_fields"]),
                "redacted_values": list(event["redacted_values"]),
                "manual_review_required": True,
                "source_text_generated": False,
                "review_questions": [
                    "Does this anchor still match the pinned commit?",
                    "Does the proposed event use only value_redacted bucket names?",
                    "Does the proposed location avoid raw secret material?",
                    "Is the event necessary for the planned leakage experiment?",
                ],
            }
        )
    proposal = {
        "format": OPENSSL_SOURCE_EDIT_PROPOSAL_FORMAT,
        "report_type": "openssl_source_edit_proposal",
        "status": "source_edit_proposal_ready",
        "experiment_id": stub["experiment_id"],
        "target_family": stub["target_family"],
        "exact_commit_sha": stub["exact_commit_sha"],
        "worktree_path": stub["worktree_path"],
        "dirty": stub["dirty"],
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "compile_allowed": False,
        "diff_generation_allowed": False,
        "patch_application_allowed": False,
        "raw_secret_capture_allowed": False,
        "trace_view": "redacted",
        "stub_api": dict(stub["stub_api"]),
        "redaction_policy": dict(stub["redaction_policy"]),
        "proposals": proposals,
        "gates": list(REQUIRED_GATES),
        "notes": [
            "This artifact proposes review slots only.",
            "It does not contain source text, diffs, or replacement text.",
            "Any later edit must be reviewed against the pinned commit and stub contract.",
        ],
    }
    validate_openssl_source_edit_proposal(proposal)
    return proposal


def validate_openssl_source_edit_proposal(proposal: dict[str, Any]) -> None:
    """Validate a review-only OpenSSL source edit proposal."""

    _require_equal(proposal.get("format"), OPENSSL_SOURCE_EDIT_PROPOSAL_FORMAT, "format")
    _require_equal(proposal.get("report_type"), "openssl_source_edit_proposal", "report_type")
    _require_equal(proposal.get("status"), "source_edit_proposal_ready", "status")
    _require_equal(proposal.get("execution_allowed"), False, "execution_allowed")
    _require_equal(proposal.get("source_mutation_allowed"), False, "source_mutation_allowed")
    _require_equal(proposal.get("compile_allowed"), False, "compile_allowed")
    _require_equal(proposal.get("diff_generation_allowed"), False, "diff_generation_allowed")
    _require_equal(proposal.get("patch_application_allowed"), False, "patch_application_allowed")
    _require_equal(proposal.get("raw_secret_capture_allowed"), False, "raw_secret_capture_allowed")
    _require_equal(proposal.get("trace_view"), "redacted", "trace_view")
    _require_string(proposal.get("experiment_id"), "experiment_id")
    _require_string(proposal.get("exact_commit_sha"), "exact_commit_sha")
    proposals = _require_list(proposal.get("proposals"), "proposals", min_items=1)
    seen_ids: set[str] = set()
    for index, item in enumerate(proposals):
        _validate_proposal_item(item, index=index, seen_ids=seen_ids)
    gates = set(_validate_string_list(proposal.get("gates"), "gates", min_items=len(REQUIRED_GATES)))
    missing_gates = sorted(set(REQUIRED_GATES) - gates)
    if missing_gates:
        raise OpenSSLSourceEditProposalError(f"gates missing: {', '.join(missing_gates)}")


def source_edit_proposal_markdown(proposal: dict[str, Any]) -> str:
    """Render a source edit proposal as Markdown."""

    validate_openssl_source_edit_proposal(proposal)
    lines = [
        "# TraceLeak OpenSSL Source Edit Proposal",
        "",
        f"- Experiment: `{proposal['experiment_id']}`",
        f"- Target family: `{proposal['target_family']}`",
        f"- Commit: `{proposal['exact_commit_sha']}`",
        f"- Worktree: `{proposal['worktree_path']}`",
        f"- Dirty: `{str(proposal['dirty']).lower()}`",
        f"- Execution allowed: `{str(proposal['execution_allowed']).lower()}`",
        f"- Source mutation allowed: `{str(proposal['source_mutation_allowed']).lower()}`",
        f"- Diff generation allowed: `{str(proposal['diff_generation_allowed']).lower()}`",
        f"- Patch application allowed: `{str(proposal['patch_application_allowed']).lower()}`",
        f"- Raw secret capture allowed: `{str(proposal['raw_secret_capture_allowed']).lower()}`",
        "",
        "## Proposed Review Slots",
        "",
        "| Proposal | Event group | Path | Anchor symbol | Anchor line | Placement policy |",
        "|---|---|---|---|---:|---|",
    ]
    for item in proposal["proposals"]:
        lines.append(
            "| `{pid}` | `{group}` | `{path}` | `{symbol}` | `{line}` | `{policy}` |".format(
                pid=item["proposal_id"],
                group=item["group_id"],
                path=item["target_path"],
                symbol=item["anchor_symbol"],
                line=item["anchor_line"],
                policy=item["placement_policy"],
            )
        )
    lines.extend(["", "## Gates", ""])
    lines.extend(f"- `{gate}`" for gate in proposal["gates"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in proposal.get("notes", []))
    lines.append("")
    return "\n".join(lines)


def write_source_edit_proposal_json(path: str | Path, proposal: dict[str, Any]) -> None:
    """Write source edit proposal JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_source_edit_proposal_markdown(path: str | Path, proposal: dict[str, Any]) -> None:
    """Write source edit proposal Markdown."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(source_edit_proposal_markdown(proposal), encoding="utf-8")


def _placement_policy(event_type: str) -> str:
    if event_type == "phase":
        return "review_near_anchor_function_entry"
    if event_type == "loop":
        return "review_inside_existing_loop"
    if event_type == "branch":
        return "review_near_result_branch"
    return "manual_review_required"


def _validate_proposal_item(item: Any, *, index: int, seen_ids: set[str]) -> None:
    if not isinstance(item, dict):
        raise OpenSSLSourceEditProposalError(f"proposals[{index}] must be an object")
    forbidden = sorted(DISALLOWED_PROPOSAL_KEYS & set(item))
    if forbidden:
        raise OpenSSLSourceEditProposalError(
            f"proposals[{index}] contains generated source fields: {', '.join(forbidden)}"
        )
    proposal_id = _require_string(item.get("proposal_id"), f"proposals[{index}].proposal_id")
    if proposal_id in seen_ids:
        raise OpenSSLSourceEditProposalError(f"duplicate proposal_id: {proposal_id}")
    seen_ids.add(proposal_id)
    _require_string(item.get("group_id"), f"proposals[{index}].group_id")
    _require_string(item.get("target_path"), f"proposals[{index}].target_path")
    _require_string(item.get("anchor_symbol"), f"proposals[{index}].anchor_symbol")
    anchor_line = item.get("anchor_line")
    if not isinstance(anchor_line, int) or anchor_line <= 0:
        raise OpenSSLSourceEditProposalError(
            f"proposals[{index}].anchor_line must be a positive integer"
        )
    _require_string(item.get("placement_policy"), f"proposals[{index}].placement_policy")
    _require_equal(item.get("manual_review_required"), True, f"proposals[{index}].manual_review_required")
    _require_equal(item.get("source_text_generated"), False, f"proposals[{index}].source_text_generated")
    _validate_string_list(item.get("payload_fields"), f"proposals[{index}].payload_fields", min_items=1)
    _validate_string_list(item.get("redacted_values"), f"proposals[{index}].redacted_values", min_items=1)
    _validate_string_list(item.get("review_questions"), f"proposals[{index}].review_questions", min_items=1)


def _require_list(value: Any, name: str, *, min_items: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise OpenSSLSourceEditProposalError(f"{name} must be a list")
    if len(value) < min_items:
        raise OpenSSLSourceEditProposalError(f"{name} must contain at least {min_items} item(s)")
    return value


def _validate_string_list(value: Any, name: str, *, min_items: int = 0) -> list[str]:
    items = _require_list(value, name, min_items=min_items)
    if not all(isinstance(item, str) and item for item in items):
        raise OpenSSLSourceEditProposalError(f"{name} must contain only non-empty strings")
    return items


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenSSLSourceEditProposalError(f"{name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise OpenSSLSourceEditProposalError(f"{name} must be {expected!r}")
