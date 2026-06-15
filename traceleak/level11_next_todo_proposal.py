"""Level 11 next-TODO proposal for Level 10 review packets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level10_review_packet import (
    LEVEL10_REVIEW_PACKET_FORMAT,
    validate_level10_review_packet,
)

LEVEL11_NEXT_TODO_PROPOSAL_FORMAT = "traceleak.level11_next_todo_proposal.v1"
LEVEL11_NEXT_TODO_PROPOSAL_PHASE = "P129"
LEVEL11_NEXT_TODO_REPORT_PHASE = "P130"


class Level11NextTodoProposalError(ValueError):
    """Raised when Level 11 next-TODO proposal data is invalid."""


def build_level11_next_todo_proposal(
    *,
    review_packet: dict[str, Any],
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a next-TODO proposal from a validated Level 10 review packet."""

    validate_level10_review_packet(review_packet)
    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    ready = review_packet["review_items"]["ready_for_next_todo"] is True
    proposal = {
        "format": LEVEL11_NEXT_TODO_PROPOSAL_FORMAT,
        "phase": LEVEL11_NEXT_TODO_PROPOSAL_PHASE,
        "source_packet_format": review_packet["format"],
        "source_packet_phase": review_packet["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "proposal_status": "ready_for_todo_draft" if ready else "blocked_by_missing_artifacts",
        "readiness": dict(review_packet["readiness"]),
        "missing_artifacts": list(review_packet["missing_artifacts"]),
        "recommended_next_todo": {
            "level": 12,
            "scope": "draft_next_review_checkpoint" if ready else "complete_missing_artifacts",
            "requires_new_review": True,
        },
        "allowances": {
            "proposal_only": True,
            "direct_action_enabled": False,
            "content_read_enabled": False,
            "claim_enabled": False,
        },
    }
    validate_level11_next_todo_proposal(proposal)
    return proposal


def validate_level11_next_todo_proposal(proposal: dict[str, Any]) -> None:
    """Validate Level 11 next-TODO proposal shape."""

    if not isinstance(proposal, dict):
        raise Level11NextTodoProposalError("proposal must be an object")
    _eq(proposal.get("format"), LEVEL11_NEXT_TODO_PROPOSAL_FORMAT, "proposal.format")
    _eq(proposal.get("phase"), LEVEL11_NEXT_TODO_PROPOSAL_PHASE, "proposal.phase")
    _eq(proposal.get("source_packet_format"), LEVEL10_REVIEW_PACKET_FORMAT, "proposal.source_packet_format")
    _non_empty(proposal.get("reviewer"), "proposal.reviewer")
    _non_empty(proposal.get("reviewed_at"), "proposal.reviewed_at")
    if proposal.get("proposal_status") not in {"ready_for_todo_draft", "blocked_by_missing_artifacts"}:
        raise Level11NextTodoProposalError("proposal.proposal_status is invalid")
    readiness = proposal.get("readiness")
    if not isinstance(readiness, dict):
        raise Level11NextTodoProposalError("proposal.readiness must be an object")
    if readiness.get("status") not in {"ready", "incomplete"}:
        raise Level11NextTodoProposalError("proposal.readiness.status is invalid")
    expected_status = (
        "ready_for_todo_draft" if readiness["status"] == "ready" else "blocked_by_missing_artifacts"
    )
    _eq(proposal.get("proposal_status"), expected_status, "proposal.proposal_status")
    ratio = readiness.get("readiness_ratio")
    if not isinstance(ratio, int | float) or ratio < 0 or ratio > 1:
        raise Level11NextTodoProposalError("proposal.readiness.readiness_ratio must be between 0 and 1")
    for key in ["entry_count", "present_count", "missing_count"]:
        if not isinstance(readiness.get(key), int) or readiness[key] < 0:
            raise Level11NextTodoProposalError(f"proposal.readiness.{key} must be a non-negative integer")
    _eq(readiness["present_count"] + readiness["missing_count"], readiness["entry_count"], "proposal.readiness.counts")
    missing = proposal.get("missing_artifacts")
    if not isinstance(missing, list):
        raise Level11NextTodoProposalError("proposal.missing_artifacts must be a list")
    _eq(len(missing), readiness["missing_count"], "proposal.missing_artifacts length")
    next_todo = proposal.get("recommended_next_todo")
    if not isinstance(next_todo, dict):
        raise Level11NextTodoProposalError("proposal.recommended_next_todo must be an object")
    _eq(next_todo.get("level"), 12, "proposal.recommended_next_todo.level")
    expected_scope = "draft_next_review_checkpoint" if readiness["status"] == "ready" else "complete_missing_artifacts"
    _eq(next_todo.get("scope"), expected_scope, "proposal.recommended_next_todo.scope")
    _eq(next_todo.get("requires_new_review"), True, "proposal.recommended_next_todo.requires_new_review")
    allowances = proposal.get("allowances")
    if not isinstance(allowances, dict):
        raise Level11NextTodoProposalError("proposal.allowances must be an object")
    _eq(allowances.get("proposal_only"), True, "proposal.allowances.proposal_only")
    for key in ["direct_action_enabled", "content_read_enabled", "claim_enabled"]:
        _eq(allowances.get(key), False, f"proposal.allowances.{key}")


def render_level11_next_todo_report(proposal: dict[str, Any]) -> str:
    """Render a Markdown report for a Level 11 next-TODO proposal."""

    validate_level11_next_todo_proposal(proposal)
    lines = [
        "# Level 11 Next TODO Proposal",
        "",
        f"- Phase: `{LEVEL11_NEXT_TODO_REPORT_PHASE}`",
        f"- Source packet: `{proposal['source_packet_format']}`",
        f"- Proposal status: `{proposal['proposal_status']}`",
        "",
        "## Readiness",
        "",
        f"- Status: `{proposal['readiness']['status']}`",
        f"- Ratio: `{proposal['readiness']['readiness_ratio']}`",
        f"- Entries: `{proposal['readiness']['entry_count']}`",
        f"- Present: `{proposal['readiness']['present_count']}`",
        f"- Missing: `{proposal['readiness']['missing_count']}`",
        "",
        "## Recommended next TODO",
        "",
        f"- Level: `{proposal['recommended_next_todo']['level']}`",
        f"- Scope: `{proposal['recommended_next_todo']['scope']}`",
        f"- Requires new review: `{proposal['recommended_next_todo']['requires_new_review']}`",
        "",
        "## Allowances",
        "",
        "Proposal only: `True`",
        "Direct action enabled: `False`",
        "Content read enabled: `False`",
        "Claim enabled: `False`",
        "",
    ]
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level11_next_todo_report(markdown)
    return markdown


def validate_level11_next_todo_report(markdown: str) -> None:
    """Validate Level 11 next-TODO Markdown report."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level11NextTodoProposalError("markdown must be a newline-terminated string")
    for text in [
        "# Level 11 Next TODO Proposal",
        "## Readiness",
        "## Recommended next TODO",
        "## Allowances",
        "Proposal only: `True`",
        "Direct action enabled: `False`",
        "Content read enabled: `False`",
        "Claim enabled: `False`",
    ]:
        if text not in markdown:
            raise Level11NextTodoProposalError(f"missing markdown text: {text}")


def write_level11_next_todo_proposal(path: Path, proposal: dict[str, Any]) -> None:
    """Write Level 11 next-TODO proposal JSON."""

    validate_level11_next_todo_proposal(proposal)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level11_next_todo_report(path: Path, markdown: str) -> None:
    """Write Level 11 next-TODO Markdown report."""

    validate_level11_next_todo_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level11NextTodoProposalError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level11NextTodoProposalError(f"{name} must be {expected!r}")
