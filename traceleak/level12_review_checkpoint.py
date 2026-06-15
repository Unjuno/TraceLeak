"""Level 12 review checkpoint from Level 11 next-TODO proposals."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traceleak.level11_next_todo_proposal import (
    LEVEL11_NEXT_TODO_PROPOSAL_FORMAT,
    validate_level11_next_todo_proposal,
)

LEVEL12_REVIEW_CHECKPOINT_FORMAT = "traceleak.level12_review_checkpoint.v1"
LEVEL12_REVIEW_CHECKPOINT_PHASE = "P133"
LEVEL12_REVIEW_CHECKPOINT_REPORT_PHASE = "P134"


class Level12ReviewCheckpointError(ValueError):
    """Raised when Level 12 review checkpoint data is invalid."""


def build_level12_review_checkpoint(
    *,
    next_todo_proposal: dict[str, Any],
    checkpoint_id: str = "level12-review-checkpoint",
    reviewer: str = "reviewer",
    reviewed_at: str = "2026-06-15T00:00:00Z",
) -> dict[str, Any]:
    """Build a review checkpoint from a validated Level 11 proposal."""

    validate_level11_next_todo_proposal(next_todo_proposal)
    checkpoint_id = _non_empty(checkpoint_id, "checkpoint_id")
    reviewer = _non_empty(reviewer, "reviewer")
    reviewed_at = _non_empty(reviewed_at, "reviewed_at")
    ready = next_todo_proposal["proposal_status"] == "ready_for_todo_draft"
    checkpoint = {
        "format": LEVEL12_REVIEW_CHECKPOINT_FORMAT,
        "phase": LEVEL12_REVIEW_CHECKPOINT_PHASE,
        "checkpoint_id": checkpoint_id,
        "source_proposal_format": next_todo_proposal["format"],
        "source_proposal_phase": next_todo_proposal["phase"],
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "checkpoint_status": "ready_for_level12_todo" if ready else "blocked_by_level11_proposal",
        "source_readiness": dict(next_todo_proposal["readiness"]),
        "source_recommendation": dict(next_todo_proposal["recommended_next_todo"]),
        "required_preconditions": {
            "focused_tests_passed": False,
            "ruff_passed": False,
            "full_pytest_passed": False,
            "new_review_recorded": True,
        },
        "allowances": {
            "checkpoint_only": True,
            "direct_action_enabled": False,
            "content_read_enabled": False,
            "claim_enabled": False,
        },
        "notes": [
            "This checkpoint records whether the next TODO may be drafted.",
            "It does not broaden behavior beyond local review artifacts.",
        ],
    }
    validate_level12_review_checkpoint(checkpoint)
    return checkpoint


def validate_level12_review_checkpoint(checkpoint: dict[str, Any]) -> None:
    """Validate Level 12 review checkpoint shape."""

    if not isinstance(checkpoint, dict):
        raise Level12ReviewCheckpointError("checkpoint must be an object")
    _eq(checkpoint.get("format"), LEVEL12_REVIEW_CHECKPOINT_FORMAT, "checkpoint.format")
    _eq(checkpoint.get("phase"), LEVEL12_REVIEW_CHECKPOINT_PHASE, "checkpoint.phase")
    _non_empty(checkpoint.get("checkpoint_id"), "checkpoint.checkpoint_id")
    _eq(
        checkpoint.get("source_proposal_format"),
        LEVEL11_NEXT_TODO_PROPOSAL_FORMAT,
        "checkpoint.source_proposal_format",
    )
    _non_empty(checkpoint.get("reviewer"), "checkpoint.reviewer")
    _non_empty(checkpoint.get("reviewed_at"), "checkpoint.reviewed_at")
    if checkpoint.get("checkpoint_status") not in {
        "ready_for_level12_todo",
        "blocked_by_level11_proposal",
    }:
        raise Level12ReviewCheckpointError("checkpoint.checkpoint_status is invalid")
    readiness = checkpoint.get("source_readiness")
    if not isinstance(readiness, dict):
        raise Level12ReviewCheckpointError("checkpoint.source_readiness must be an object")
    if readiness.get("status") not in {"ready", "incomplete"}:
        raise Level12ReviewCheckpointError("checkpoint.source_readiness.status is invalid")
    expected_status = (
        "ready_for_level12_todo" if readiness["status"] == "ready" else "blocked_by_level11_proposal"
    )
    _eq(checkpoint.get("checkpoint_status"), expected_status, "checkpoint.checkpoint_status")
    recommendation = checkpoint.get("source_recommendation")
    if not isinstance(recommendation, dict):
        raise Level12ReviewCheckpointError("checkpoint.source_recommendation must be an object")
    _eq(recommendation.get("level"), 12, "checkpoint.source_recommendation.level")
    if recommendation.get("scope") not in {"draft_next_review_checkpoint", "complete_missing_artifacts"}:
        raise Level12ReviewCheckpointError("checkpoint.source_recommendation.scope is invalid")
    _eq(
        recommendation.get("requires_new_review"),
        True,
        "checkpoint.source_recommendation.requires_new_review",
    )
    preconditions = checkpoint.get("required_preconditions")
    if not isinstance(preconditions, dict):
        raise Level12ReviewCheckpointError("checkpoint.required_preconditions must be an object")
    _eq(preconditions.get("focused_tests_passed"), False, "checkpoint.required_preconditions.focused_tests_passed")
    _eq(preconditions.get("ruff_passed"), False, "checkpoint.required_preconditions.ruff_passed")
    _eq(preconditions.get("full_pytest_passed"), False, "checkpoint.required_preconditions.full_pytest_passed")
    _eq(preconditions.get("new_review_recorded"), True, "checkpoint.required_preconditions.new_review_recorded")
    allowances = checkpoint.get("allowances")
    if not isinstance(allowances, dict):
        raise Level12ReviewCheckpointError("checkpoint.allowances must be an object")
    _eq(allowances.get("checkpoint_only"), True, "checkpoint.allowances.checkpoint_only")
    for key in ["direct_action_enabled", "content_read_enabled", "claim_enabled"]:
        _eq(allowances.get(key), False, f"checkpoint.allowances.{key}")
    notes = checkpoint.get("notes")
    if not isinstance(notes, list) or len(notes) < 2:
        raise Level12ReviewCheckpointError("checkpoint.notes must contain at least two notes")


def render_level12_review_checkpoint_report(checkpoint: dict[str, Any]) -> str:
    """Render a Markdown report for a Level 12 review checkpoint."""

    validate_level12_review_checkpoint(checkpoint)
    lines = [
        "# Level 12 Review Checkpoint",
        "",
        f"- Phase: `{LEVEL12_REVIEW_CHECKPOINT_REPORT_PHASE}`",
        f"- Checkpoint ID: `{checkpoint['checkpoint_id']}`",
        f"- Status: `{checkpoint['checkpoint_status']}`",
        f"- Source proposal: `{checkpoint['source_proposal_format']}`",
        "",
        "## Source readiness",
        "",
        f"- Status: `{checkpoint['source_readiness']['status']}`",
        f"- Ratio: `{checkpoint['source_readiness']['readiness_ratio']}`",
        f"- Missing: `{checkpoint['source_readiness']['missing_count']}`",
        "",
        "## Required preconditions",
        "",
        f"- Focused tests passed: `{checkpoint['required_preconditions']['focused_tests_passed']}`",
        f"- Ruff passed: `{checkpoint['required_preconditions']['ruff_passed']}`",
        f"- Full pytest passed: `{checkpoint['required_preconditions']['full_pytest_passed']}`",
        f"- New review recorded: `{checkpoint['required_preconditions']['new_review_recorded']}`",
        "",
        "## Allowances",
        "",
        "Checkpoint only: `True`",
        "Direct action enabled: `False`",
        "Content read enabled: `False`",
        "Claim enabled: `False`",
        "",
    ]
    markdown = "\n".join(lines)
    if not markdown.endswith("\n"):
        markdown += "\n"
    validate_level12_review_checkpoint_report(markdown)
    return markdown


def validate_level12_review_checkpoint_report(markdown: str) -> None:
    """Validate Level 12 review checkpoint Markdown."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise Level12ReviewCheckpointError("markdown must be a newline-terminated string")
    for text in [
        "# Level 12 Review Checkpoint",
        "## Source readiness",
        "## Required preconditions",
        "## Allowances",
        "Checkpoint only: `True`",
        "Direct action enabled: `False`",
        "Content read enabled: `False`",
        "Claim enabled: `False`",
    ]:
        if text not in markdown:
            raise Level12ReviewCheckpointError(f"missing markdown text: {text}")


def write_level12_review_checkpoint(path: Path, checkpoint: dict[str, Any]) -> None:
    """Write Level 12 review checkpoint JSON."""

    validate_level12_review_checkpoint(checkpoint)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_level12_review_checkpoint_report(path: Path, markdown: str) -> None:
    """Write Level 12 review checkpoint Markdown."""

    validate_level12_review_checkpoint_report(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Level12ReviewCheckpointError(f"{name} must be a non-empty string")
    return value.strip()


def _eq(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise Level12ReviewCheckpointError(f"{name} must be {expected!r}")
