import json

import pytest

from traceleak.level10_review_packet import LEVEL10_REVIEW_PACKET_FORMAT
from traceleak.level11_next_todo_proposal import (
    LEVEL11_NEXT_TODO_PROPOSAL_FORMAT,
    Level11NextTodoProposalError,
    build_level11_next_todo_proposal,
    render_level11_next_todo_report,
    validate_level11_next_todo_proposal,
    validate_level11_next_todo_report,
    write_level11_next_todo_proposal,
    write_level11_next_todo_report,
)


def review_packet(*, ready: bool = True):
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
        "format": LEVEL10_REVIEW_PACKET_FORMAT,
        "phase": "P125",
        "source_audit_format": "traceleak.level9_readiness_audit.v1",
        "source_audit_phase": "P121",
        "reviewer": "reviewer",
        "reviewed_at": "2026-06-15T00:00:00Z",
        "readiness": {
            "status": "ready" if ready else "incomplete",
            "readiness_ratio": 1.0 if ready else 0.5,
            "entry_count": 2,
            "present_count": 2 if ready else 1,
            "missing_count": 0 if ready else 1,
        },
        "missing_artifacts": missing,
        "review_items": {
            "path_only_confirmed": True,
            "payload_read_confirmed_false": True,
            "claim_generated_confirmed_false": True,
            "ready_for_next_todo": ready,
        },
        "allowances": {
            "review_packet_only": True,
            "direct_action_enabled": False,
            "content_read_enabled": False,
            "claim_enabled": False,
        },
    }


def test_next_todo_proposal_ready_packet() -> None:
    proposal = build_level11_next_todo_proposal(review_packet=review_packet())

    assert proposal["format"] == LEVEL11_NEXT_TODO_PROPOSAL_FORMAT
    assert proposal["phase"] == "P129"
    assert proposal["proposal_status"] == "ready_for_todo_draft"
    assert proposal["recommended_next_todo"]["level"] == 12
    assert proposal["recommended_next_todo"]["scope"] == "draft_next_review_checkpoint"
    assert proposal["recommended_next_todo"]["requires_new_review"] is True
    assert proposal["allowances"]["proposal_only"] is True
    assert proposal["allowances"]["direct_action_enabled"] is False
    assert proposal["allowances"]["content_read_enabled"] is False
    assert proposal["allowances"]["claim_enabled"] is False
    validate_level11_next_todo_proposal(proposal)


def test_next_todo_proposal_blocked_packet() -> None:
    proposal = build_level11_next_todo_proposal(review_packet=review_packet(ready=False))

    assert proposal["proposal_status"] == "blocked_by_missing_artifacts"
    assert proposal["recommended_next_todo"]["scope"] == "complete_missing_artifacts"
    assert proposal["missing_artifacts"][0]["key"] == "missing"


def test_next_todo_proposal_rejects_content_read_enabled() -> None:
    proposal = build_level11_next_todo_proposal(review_packet=review_packet())
    proposal["allowances"]["content_read_enabled"] = True

    with pytest.raises(Level11NextTodoProposalError, match="content_read_enabled"):
        validate_level11_next_todo_proposal(proposal)


def test_next_todo_report_renders_required_sections() -> None:
    proposal = build_level11_next_todo_proposal(review_packet=review_packet())

    markdown = render_level11_next_todo_report(proposal)

    assert "# Level 11 Next TODO Proposal" in markdown
    assert "## Recommended next TODO" in markdown
    assert "Proposal only: `True`" in markdown
    assert "Direct action enabled: `False`" in markdown
    assert "Content read enabled: `False`" in markdown
    assert "Claim enabled: `False`" in markdown
    validate_level11_next_todo_report(markdown)


def test_next_todo_writers(tmp_path) -> None:
    proposal = build_level11_next_todo_proposal(review_packet=review_packet())
    markdown = render_level11_next_todo_report(proposal)
    proposal_path = tmp_path / "level11-next-todo-proposal.json"
    report_path = tmp_path / "level11-next-todo-proposal.md"

    write_level11_next_todo_proposal(proposal_path, proposal)
    write_level11_next_todo_report(report_path, markdown)

    assert json.loads(proposal_path.read_text(encoding="utf-8"))["format"] == LEVEL11_NEXT_TODO_PROPOSAL_FORMAT
    assert report_path.read_text(encoding="utf-8").startswith("# Level 11 Next TODO Proposal")
