import json

import pytest

from traceleak.level11_next_todo_proposal import LEVEL11_NEXT_TODO_PROPOSAL_FORMAT
from traceleak.level12_review_checkpoint import (
    LEVEL12_REVIEW_CHECKPOINT_FORMAT,
    Level12ReviewCheckpointError,
    build_level12_review_checkpoint,
    render_level12_review_checkpoint_report,
    validate_level12_review_checkpoint,
    validate_level12_review_checkpoint_report,
    write_level12_review_checkpoint,
    write_level12_review_checkpoint_report,
)


def proposal(*, ready: bool = True):
    missing = []
    if not ready:
        missing = [
            {
                "key": "missing",
                "artifact_class": "summary_json",
                "relative_path": "reports/local/missing.json",
                "role": "missing summary",
            }
        ]
    return {
        "format": LEVEL11_NEXT_TODO_PROPOSAL_FORMAT,
        "phase": "P129",
        "source_packet_format": "traceleak.level10_review_packet.v1",
        "source_packet_phase": "P125",
        "reviewer": "reviewer",
        "reviewed_at": "2026-06-15T00:00:00Z",
        "proposal_status": "ready_for_todo_draft" if ready else "blocked_by_missing_artifacts",
        "readiness": {
            "status": "ready" if ready else "incomplete",
            "readiness_ratio": 1.0 if ready else 0.5,
            "entry_count": 2,
            "present_count": 2 if ready else 1,
            "missing_count": 0 if ready else 1,
        },
        "missing_artifacts": missing,
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


def test_review_checkpoint_ready_proposal() -> None:
    checkpoint = build_level12_review_checkpoint(next_todo_proposal=proposal())

    assert checkpoint["format"] == LEVEL12_REVIEW_CHECKPOINT_FORMAT
    assert checkpoint["phase"] == "P133"
    assert checkpoint["checkpoint_status"] == "ready_for_level12_todo"
    assert checkpoint["allowances"]["checkpoint_only"] is True
    assert checkpoint["allowances"]["direct_action_enabled"] is False
    assert checkpoint["allowances"]["content_read_enabled"] is False
    assert checkpoint["allowances"]["claim_enabled"] is False
    validate_level12_review_checkpoint(checkpoint)


def test_review_checkpoint_blocked_proposal() -> None:
    checkpoint = build_level12_review_checkpoint(next_todo_proposal=proposal(ready=False))

    assert checkpoint["checkpoint_status"] == "blocked_by_level11_proposal"
    assert checkpoint["source_readiness"]["status"] == "incomplete"
    assert checkpoint["source_recommendation"]["scope"] == "complete_missing_artifacts"


def test_review_checkpoint_rejects_direct_action_enabled() -> None:
    checkpoint = build_level12_review_checkpoint(next_todo_proposal=proposal())
    checkpoint["allowances"]["direct_action_enabled"] = True

    with pytest.raises(Level12ReviewCheckpointError, match="direct_action_enabled"):
        validate_level12_review_checkpoint(checkpoint)


def test_review_checkpoint_report_renders_required_sections() -> None:
    checkpoint = build_level12_review_checkpoint(next_todo_proposal=proposal())

    markdown = render_level12_review_checkpoint_report(checkpoint)

    assert "# Level 12 Review Checkpoint" in markdown
    assert "## Source readiness" in markdown
    assert "## Required preconditions" in markdown
    assert "Checkpoint only: `True`" in markdown
    assert "Direct action enabled: `False`" in markdown
    assert "Content read enabled: `False`" in markdown
    assert "Claim enabled: `False`" in markdown
    validate_level12_review_checkpoint_report(markdown)


def test_review_checkpoint_writers(tmp_path) -> None:
    checkpoint = build_level12_review_checkpoint(next_todo_proposal=proposal())
    markdown = render_level12_review_checkpoint_report(checkpoint)
    checkpoint_path = tmp_path / "level12-review-checkpoint.json"
    report_path = tmp_path / "level12-review-checkpoint.md"

    write_level12_review_checkpoint(checkpoint_path, checkpoint)
    write_level12_review_checkpoint_report(report_path, markdown)

    assert json.loads(checkpoint_path.read_text(encoding="utf-8"))["format"] == LEVEL12_REVIEW_CHECKPOINT_FORMAT
    assert report_path.read_text(encoding="utf-8").startswith("# Level 12 Review Checkpoint")
