from traceleak.level24_index import (
    build_level24_index,
    render_level24_index_report,
    validate_level24_index_report,
    write_level24_index_report,
)


def test_level24_index_report_sections() -> None:
    index = build_level24_index()

    markdown = render_level24_index_report(index)

    assert "# Level 24 Index Report" in markdown
    assert "## Output paths" in markdown
    assert "## Review-only boundary" in markdown
    assert "## Expected validation commands" in markdown
    assert "## Next-level preconditions" in markdown
    assert "Review only: `True`" in markdown
    assert "Path only: `True`" in markdown
    validate_level24_index_report(markdown)


def test_level24_index_report_writer(tmp_path) -> None:
    index = build_level24_index()
    markdown = render_level24_index_report(index)
    path = tmp_path / "level24-index-report.md"

    write_level24_index_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 24 Index Report")
