import json

import pytest

from traceleak.level14_completeness import LEVEL14_COMPLETENESS_AUDIT_FORMAT
from traceleak.level15_validation_rollup import (
    EXPECTED_VALIDATION_COMMANDS,
    LEVEL15_VALIDATION_ROLLUP_FORMAT,
    Level15ValidationRollupError,
    build_level15_validation_rollup,
    validate_level15_validation_rollup,
    write_level15_validation_rollup,
)


def audit(*, complete: bool = True):
    missing = [] if complete else ["level10_review"]
    observed = [
        "level6_profile",
        "level7_planning",
        "level8_intake",
        "level9_readiness",
        "level10_review",
        "level11_next_todo",
        "level12_checkpoint",
    ]
    if not complete:
        observed.remove("level10_review")
    return {
        "format": LEVEL14_COMPLETENESS_AUDIT_FORMAT,
        "phase": "P143",
        "source_inventory_format": "traceleak.level13_handoff_inventory.v1",
        "source_inventory_phase": "P138",
        "required_families": [
            "level6_profile",
            "level7_planning",
            "level8_intake",
            "level9_readiness",
            "level10_review",
            "level11_next_todo",
            "level12_checkpoint",
        ],
        "observed_families": observed,
        "family_count": len(observed),
        "path_count": len(observed),
        "missing_required_families": missing,
        "completeness_status": "complete" if complete else "incomplete",
        "flags": {"path_only": True, "content_read": False, "claim_generated": False},
    }


def test_validation_rollup_complete_audit() -> None:
    rollup = build_level15_validation_rollup(completeness_audit=audit())

    assert rollup["format"] == LEVEL15_VALIDATION_ROLLUP_FORMAT
    assert rollup["phase"] == "P148"
    assert rollup["source_completeness_status"] == "complete"
    assert rollup["validation_status"] == "pending"
    assert rollup["expected_validation_commands"] == EXPECTED_VALIDATION_COMMANDS
    assert all(item["status"] == "pending" for item in rollup["validation_results"])
    assert rollup["flags"]["review_only"] is True
    assert rollup["flags"]["path_only"] is True
    assert rollup["flags"]["content_read"] is False
    assert rollup["flags"]["command_executed"] is False
    assert rollup["flags"]["claim_generated"] is False
    validate_level15_validation_rollup(rollup)


def test_validation_rollup_incomplete_audit() -> None:
    rollup = build_level15_validation_rollup(completeness_audit=audit(complete=False))

    assert rollup["source_completeness_status"] == "incomplete"
    assert rollup["validation_status"] == "pending"


def test_validation_rollup_rejects_command_executed_enabled() -> None:
    rollup = build_level15_validation_rollup(completeness_audit=audit())
    rollup["flags"]["command_executed"] = True

    with pytest.raises(Level15ValidationRollupError, match="command_executed"):
        validate_level15_validation_rollup(rollup)


def test_validation_rollup_rejects_content_read_enabled() -> None:
    rollup = build_level15_validation_rollup(completeness_audit=audit())
    rollup["flags"]["content_read"] = True

    with pytest.raises(Level15ValidationRollupError, match="content_read"):
        validate_level15_validation_rollup(rollup)


def test_validation_rollup_writer(tmp_path) -> None:
    rollup = build_level15_validation_rollup(completeness_audit=audit())
    path = tmp_path / "level15-validation-rollup.json"

    write_level15_validation_rollup(path, rollup)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL15_VALIDATION_ROLLUP_FORMAT
