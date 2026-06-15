from tests.test_level15_validation_rollup import audit
from traceleak.level15_validation_rollup import (
    build_level15_validation_rollup,
    render_level15_validation_rollup_report,
    validate_level15_validation_rollup_report,
    write_level15_validation_rollup_report,
)


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
