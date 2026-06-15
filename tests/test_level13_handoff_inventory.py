import json

import pytest

from traceleak.level12_review_checkpoint import LEVEL12_REVIEW_CHECKPOINT_FORMAT
from traceleak.level13_closure import (
    LEVEL13_HANDOFF_INVENTORY_FORMAT,
    Level13ClosureError,
    build_level13_closure_manifest,
    build_level13_handoff_inventory,
    validate_level13_handoff_inventory,
    write_level13_handoff_inventory,
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


def manifest():
    return build_level13_closure_manifest(review_checkpoint=checkpoint())


def test_handoff_inventory_default_families() -> None:
    inventory = build_level13_handoff_inventory(closure_manifest=manifest())

    assert inventory["format"] == LEVEL13_HANDOFF_INVENTORY_FORMAT
    assert inventory["phase"] == "P138"
    assert inventory["closure_status"] == "ready_for_handoff"
    assert len(inventory["families"]) >= 7
    assert inventory["flags"]["path_only"] is True
    assert inventory["flags"]["content_read"] is False
    assert inventory["flags"]["claim_generated"] is False
    validate_level13_handoff_inventory(inventory)


def test_handoff_inventory_rejects_unsafe_path() -> None:
    families = [
        {
            "family": "unsafe",
            "role": "unsafe family",
            "paths": ["../reports/local/unsafe.json"],
        }
    ]

    with pytest.raises(Level13ClosureError, match="relative"):
        build_level13_handoff_inventory(closure_manifest=manifest(), families=families)


def test_handoff_inventory_rejects_duplicate_family() -> None:
    families = [
        {
            "family": "dup",
            "role": "family a",
            "paths": ["reports/local/a.json"],
        },
        {
            "family": "dup",
            "role": "family b",
            "paths": ["reports/local/b.json"],
        },
    ]

    with pytest.raises(Level13ClosureError, match="unique"):
        build_level13_handoff_inventory(closure_manifest=manifest(), families=families)


def test_handoff_inventory_writer(tmp_path) -> None:
    inventory = build_level13_handoff_inventory(closure_manifest=manifest())
    path = tmp_path / "level13-handoff-inventory.json"

    write_level13_handoff_inventory(path, inventory)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL13_HANDOFF_INVENTORY_FORMAT
