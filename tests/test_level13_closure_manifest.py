import json

import pytest

from traceleak.level12_review_checkpoint import LEVEL12_REVIEW_CHECKPOINT_FORMAT
from traceleak.level13_closure import (
    LEVEL13_CLOSURE_MANIFEST_FORMAT,
    Level13ClosureError,
    build_level13_closure_manifest,
    validate_level13_closure_manifest,
    write_level13_closure_manifest,
)


def checkpoint(*, ready: bool = True):
    return {
        "format": LEVEL12_REVIEW_CHECKPOINT_FORMAT,
        "phase": "P133",
        "checkpoint_id": "level12-review-checkpoint",
        "source_proposal_format": "traceleak.level11_next_todo_proposal.v1",
        "source_proposal_phase": "P129",
        "reviewer": "reviewer",
        "reviewed_at": "2026-06-15T00:00:00Z",
        "checkpoint_status": "ready_for_level12_todo" if ready else "blocked_by_level11_proposal",
        "source_readiness": {
            "status": "ready" if ready else "incomplete",
            "readiness_ratio": 1.0 if ready else 0.5,
            "entry_count": 2,
            "present_count": 2 if ready else 1,
            "missing_count": 0 if ready else 1,
        },
        "source_recommendation": {
            "level": 12,
            "scope": "draft_next_review_checkpoint" if ready else "complete_missing_artifacts",
            "requires_new_review": True,
        },
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


def test_closure_manifest_ready_checkpoint() -> None:
    manifest = build_level13_closure_manifest(review_checkpoint=checkpoint())

    assert manifest["format"] == LEVEL13_CLOSURE_MANIFEST_FORMAT
    assert manifest["phase"] == "P137"
    assert manifest["closure_status"] == "ready_for_handoff"
    assert manifest["allowances"]["closure_only"] is True
    assert manifest["allowances"]["direct_action_enabled"] is False
    assert manifest["allowances"]["content_read_enabled"] is False
    assert manifest["allowances"]["claim_enabled"] is False
    validate_level13_closure_manifest(manifest)


def test_closure_manifest_blocked_checkpoint() -> None:
    manifest = build_level13_closure_manifest(review_checkpoint=checkpoint(ready=False))

    assert manifest["checkpoint_status"] == "blocked_by_level11_proposal"
    assert manifest["closure_status"] == "blocked_by_checkpoint"


def test_closure_manifest_rejects_content_read_enabled() -> None:
    manifest = build_level13_closure_manifest(review_checkpoint=checkpoint())
    manifest["allowances"]["content_read_enabled"] = True

    with pytest.raises(Level13ClosureError, match="content_read_enabled"):
        validate_level13_closure_manifest(manifest)


def test_closure_manifest_writer(tmp_path) -> None:
    manifest = build_level13_closure_manifest(review_checkpoint=checkpoint())
    path = tmp_path / "level13-closure-manifest.json"

    write_level13_closure_manifest(path, manifest)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL13_CLOSURE_MANIFEST_FORMAT
