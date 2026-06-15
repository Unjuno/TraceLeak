from traceleak.level15_validation_rollup import EXPECTED_VALIDATION_COMMANDS, LEVEL15_VALIDATION_ROLLUP_FORMAT
from traceleak.level16_pre_handoff_review import (
    build_level16_pre_handoff_review,
    render_level16_pre_handoff_review_report,
    validate_level16_pre_handoff_review_report,
    write_level16_pre_handoff_review_report,
)


def rollup():
    return {
        "format": LEVEL15_VALIDATION_ROLLUP_FORMAT,
        "phase": "P148",
        "source_audit_format": "traceleak.level14_completeness_audit.v1",
        "source_audit_phase": "P143",
        "reviewer": "reviewer",
        "reviewed_at": "2026-06-15T00:00:00Z",
        "source_completeness_status": "complete",
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


def test_review_report_sections() -> None:
    review = build_level16_pre_handoff_review(validation_rollup=rollup())
    markdown = render_level16_pre_handoff_review_report(review)

    assert "# Level 16 Pre-Handoff Review Report" in markdown
    assert "## Expected validation commands" in markdown
    assert "## Review-only boundary" in markdown
    assert "Review only: `True`" in markdown
    assert "Content read: `False`" in markdown
    assert "Command executed: `False`" in markdown
    assert "Claim generated: `False`" in markdown
    validate_level16_pre_handoff_review_report(markdown)


def test_review_report_writer(tmp_path) -> None:
    review = build_level16_pre_handoff_review(validation_rollup=rollup())
    markdown = render_level16_pre_handoff_review_report(review)
    path = tmp_path / "level16-review-report.md"

    write_level16_pre_handoff_review_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 16 Pre-Handoff Review Report")
