from traceleak.level18_archive_index import build_level18_archive_index
from traceleak.level19_summary import (
    build_level19_summary,
    render_level19_summary_report,
    validate_level19_summary_report,
    write_level19_summary_report,
)


def test_level19_summary_report_sections() -> None:
    summary = build_level19_summary(archive_index=build_level18_archive_index())

    markdown = render_level19_summary_report(summary)

    assert "# Level 19 Summary Report" in markdown
    assert "## Reviewed levels" in markdown
    assert "## Review-only boundary" in markdown
    assert "## Expected validation commands" in markdown
    assert "## Next-level preconditions" in markdown
    assert "Review only: `True`" in markdown
    assert "Path only: `True`" in markdown
    assert "Content read: `False`" in markdown
    assert "Command executed: `False`" in markdown
    validate_level19_summary_report(markdown)


def test_level19_summary_report_writer(tmp_path) -> None:
    summary = build_level19_summary(archive_index=build_level18_archive_index())
    markdown = render_level19_summary_report(summary)
    path = tmp_path / "level19-summary-report.md"

    write_level19_summary_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 19 Summary Report")
