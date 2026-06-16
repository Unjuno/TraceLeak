import json

import pytest

from traceleak.level17_release_readiness import (
    EXPECTED_LEVEL17_COMMANDS,
    LEVEL16_LOCAL_REVIEW_FORMAT,
    LEVEL17_RELEASE_READINESS_FORMAT,
    Level17ReleaseReadinessError,
    build_level17_release_readiness,
    validate_level17_release_readiness,
    write_level17_release_readiness,
)


def level16_review():
    return {
        "format": LEVEL16_LOCAL_REVIEW_FORMAT,
        "phase": "P155",
        "reviewer": "reviewer",
        "reviewed_at": "2026-06-15T00:00:00Z",
        "status": "pending_local_validation",
        "expected_validation_commands": [
            "pytest tests/test_level16_pre_handoff_review.py",
            "pytest tests/test_level16_review_report.py",
            "pytest tests/test_write_level16_files_cli.py",
            "ruff check .",
            "pytest",
        ],
        "flags": {
            "review_only": True,
            "path_only": True,
            "content_read": False,
            "command_executed": False,
            "claim_generated": False,
        },
    }


def test_release_readiness_from_valid_level16_review() -> None:
    checklist = build_level17_release_readiness(level16_review=level16_review())

    assert checklist["format"] == LEVEL17_RELEASE_READINESS_FORMAT
    assert checklist["phase"] == "P158"
    assert checklist["source_review_format"] == LEVEL16_LOCAL_REVIEW_FORMAT
    assert checklist["source_review_status"] == "pending_local_validation"
    assert checklist["readiness_status"] == "pending_local_validation"
    assert checklist["expected_validation_commands"] == EXPECTED_LEVEL17_COMMANDS
    assert all(item["status"] == "pending" for item in checklist["readiness_items"])
    assert checklist["flags"]["review_only"] is True
    assert checklist["flags"]["path_only"] is True
    assert checklist["flags"]["content_read"] is False
    assert checklist["flags"]["command_executed"] is False
    assert checklist["flags"]["claim_generated"] is False
    validate_level17_release_readiness(checklist)


def test_release_readiness_rejects_content_read_enabled() -> None:
    checklist = build_level17_release_readiness(level16_review=level16_review())
    checklist["flags"]["content_read"] = True

    with pytest.raises(Level17ReleaseReadinessError, match="content_read"):
        validate_level17_release_readiness(checklist)


def test_release_readiness_rejects_command_executed_enabled() -> None:
    checklist = build_level17_release_readiness(level16_review=level16_review())
    checklist["flags"]["command_executed"] = True

    with pytest.raises(Level17ReleaseReadinessError, match="command_executed"):
        validate_level17_release_readiness(checklist)


def test_release_readiness_writer(tmp_path) -> None:
    checklist = build_level17_release_readiness(level16_review=level16_review())
    path = tmp_path / "level17-release-readiness.json"

    write_level17_release_readiness(path, checklist)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL17_RELEASE_READINESS_FORMAT
