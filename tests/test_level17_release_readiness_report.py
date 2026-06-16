from traceleak.level17_release_readiness import (
    LEVEL16_LOCAL_REVIEW_FORMAT,
    build_level17_release_readiness,
    render_level17_release_readiness_report,
    validate_level17_release_readiness_report,
    write_level17_release_readiness_report,
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


def test_release_readiness_report_sections() -> None:
    checklist = build_level17_release_readiness(level16_review=level16_review())

    markdown = render_level17_release_readiness_report(checklist)

    assert "# Level 17 Release-Readiness Report" in markdown
    assert "## Readiness items" in markdown
    assert "## Expected validation commands" in markdown
    assert "## Review-only boundary" in markdown
    assert "## Next-level preconditions" in markdown
    assert "Review only: `True`" in markdown
    assert "Content read: `False`" in markdown
    assert "Command executed: `False`" in markdown
    assert "Claim generated: `False`" in markdown
    validate_level17_release_readiness_report(markdown)


def test_release_readiness_report_writer(tmp_path) -> None:
    checklist = build_level17_release_readiness(level16_review=level16_review())
    markdown = render_level17_release_readiness_report(checklist)
    path = tmp_path / "level17-release-readiness-report.md"

    write_level17_release_readiness_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 17 Release-Readiness Report")
