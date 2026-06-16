from traceleak.level20_closure_index import (
    build_level20_closure_index,
    render_level20_closure_index_report,
    validate_level20_closure_index_report,
    write_level20_closure_index_report,
)


def test_closure_index_report_sections() -> None:
    index = build_level20_closure_index()

    markdown = render_level20_closure_index_report(index)

    assert "# Level 20 Closure Index Report" in markdown
    assert "## Output paths" in markdown
    assert "## Review-only boundary" in markdown
    assert "## Expected validation commands" in markdown
    assert "## Next-level preconditions" in markdown
    assert "Review only: `True`" in markdown
    assert "Path only: `True`" in markdown
    assert "Content read: `False`" in markdown
    assert "Command executed: `False`" in markdown
    validate_level20_closure_index_report(markdown)


def test_closure_index_report_writer(tmp_path) -> None:
    index = build_level20_closure_index()
    markdown = render_level20_closure_index_report(index)
    path = tmp_path / "level20-closure-index-report.md"

    write_level20_closure_index_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 20 Closure Index Report")
