import json

import pytest

from traceleak.level15_validation_rollup import (
    EXPECTED_VALIDATION_COMMANDS,
    LEVEL15_VALIDATION_ROLLUP_FORMAT,
)
from traceleak.level16_pre_handoff_review import (
    LEVEL16_PRE_HANDOFF_REVIEW_FORMAT,
    Level16PreHandoffReviewError,
    build_level16_pre_handoff_review,
    validate_level16_pre_handoff_review,
    write_level16_pre_handoff_review,
)


def rollup(*, completeness_status: str = "complete"):
    return {
        "format": LEVEL15_VALIDATION_ROLLUP_FORMAT,
        "phase": "P148",
        "source_audit_format": "traceleak.level14_completeness_audit.v1",
        "source_audit_phase": "P143",
        "reviewer": "reviewer",
        "reviewed_at": "2026-06-15T00:00:00Z",
        "source_completeness_status": completeness_status,
        "validation_status": "pending",
        "expected_validation_commands": list(EXPECTED_VALIDATION_COMMANDS),
        "validation_results": [
            {"command": command, "status": "pending"} for command in EXPECTED_VALIDATION_COMMANDS
        ],
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }


def test_pre_handoff_review_pending_rollup() -> None:
    review = build_level16_pre_handoff_review(validation_rollup=rollup())

    assert review["format"] == LEVEL16_PRE_HANDOFF_REVIEW_FORMAT
    assert review["phase"] == "P153"
    assert review["source_validation_status"] == "pending"
    assert review["review_disposition"] == "ready_after_local_validation"
    assert review["expected_validation_commands"] == EXPECTED_VALIDATION_COMMANDS
    assert review["flags"]["review_only"] is True
    assert review["flags"]["path_only"] is True
    assert review["flags"]["content_read"] is False
    assert review["flags"]["command_executed"] is False
    assert review["flags"]["claim_generated"] is False
    validate_level16_pre_handoff_review(review)


def test_pre_handoff_review_incomplete_source() -> None:
    review = build_level16_pre_handoff_review(
        validation_rollup=rollup(completeness_status="incomplete"),
    )

    assert review["source_completeness_status"] == "incomplete"
    assert review["review_disposition"] == "ready_after_local_validation"


def test_pre_handoff_review_rejects_command_executed_enabled() -> None:
    review = build_level16_pre_handoff_review(validation_rollup=rollup())
    review["flags"]["command_executed"] = True

    with pytest.raises(Level16PreHandoffReviewError, match="command_executed"):
        validate_level16_pre_handoff_review(review)


def test_pre_handoff_review_rejects_content_read_enabled() -> None:
    review = build_level16_pre_handoff_review(validation_rollup=rollup())
    review["flags"]["content_read"] = True

    with pytest.raises(Level16PreHandoffReviewError, match="content_read"):
        validate_level16_pre_handoff_review(review)


def test_pre_handoff_review_writer(tmp_path) -> None:
    review = build_level16_pre_handoff_review(validation_rollup=rollup())
    path = tmp_path / "level16-pre-handoff-review.json"

    write_level16_pre_handoff_review(path, review)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL16_PRE_HANDOFF_REVIEW_FORMAT
