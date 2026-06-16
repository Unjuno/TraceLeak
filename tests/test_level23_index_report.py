from traceleak.level23_index import (
    build_level23_index,
    render_level23_index_report,
    validate_level23_index_report,
    write_level23_index_report,
)


def test_level23_index_report_sections() -> None:
    index = build_level23_index()

    markdown = render_level23_index_report(index)

    assert "# Level 23 Index Report" in markdown
    assert "## Output paths" in markdown
    assert "## Review-only boundary" in markdown
    assert "## Expected validation commands" in markdown
    assert "## Next-level preconditions" in markdown
    assert "Review only: `True`" in markdown
    assert "Path only: `True`" in markdown
    validate_level23_index_report(markdown)


def test_level23_index_report_writer(tmp_path) -> None:
    index = build_level23_index()
    markdown = render_level23_index_report(index)
    path = tmp_path / "level23-index-report.md"

    write_level23_index_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 23 Index Report")
