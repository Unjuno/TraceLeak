from traceleak.level14_completeness import LEVEL14_COMPLETENESS_AUDIT_FORMAT
from traceleak.level15_validation_rollup import (
    build_level15_validation_rollup,
    render_level15_validation_rollup_report,
    validate_level15_validation_rollup_report,
    write_level15_validation_rollup_report,
)


def audit():
    observed = [
        "level6_profile",
        "level7_planning",
        "level8_intake",
        "level9_readiness",
        "level10_review",
        "level11_next_todo",
        "level12_checkpoint",
    ]
    return {
        "format": LEVEL14_COMPLETENESS_AUDIT_FORMAT,
        "phase": "P143",
        "source_inventory_format": "traceleak.level13_handoff_inventory.v1",
        "source_inventory_phase": "P138",
        "required_families": list(observed),
        "observed_families": list(observed),
        "family_count": len(observed),
        "path_count": len(observed),
        "missing_required_families": [],
        "completeness_status": "complete",
        "flags": {"path_only": True, "content_read": False, "claim_generated": False},
    }


def test_validation_rollup_report_renders_required_sections() -> None:
    rollup = build_level15_validation_rollup(completeness_audit=audit())

    markdown = render_level15_validation_rollup_report(rollup)

    assert "# Level 15 Validation Rollup Report" in markdown
    assert "## Expected validation commands" in markdown
    assert "## Pending validation state" in markdown
    assert "## Review-only boundary" in markdown
    assert "## Next-level preconditions" in markdown
    assert "Review only: `True`" in markdown
    assert "Path only: `True`" in markdown
    assert "Content read: `False`" in markdown
    assert "Command executed: `False`" in markdown
    assert "Claim generated: `False`" in markdown
    validate_level15_validation_rollup_report(markdown)


def test_validation_rollup_report_writer(tmp_path) -> None:
    rollup = build_level15_validation_rollup(completeness_audit=audit())
    markdown = render_level15_validation_rollup_report(rollup)
    path = tmp_path / "level15-validation-rollup-report.md"

    write_level15_validation_rollup_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 15 Validation Rollup Report")
