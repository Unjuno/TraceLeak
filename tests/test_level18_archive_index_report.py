from traceleak.level18_archive_index import (
    build_level18_archive_index,
    render_level18_archive_index_report,
    validate_level18_archive_index_report,
    write_level18_archive_index_report,
)


def test_archive_index_report_sections() -> None:
    index = build_level18_archive_index()

    markdown = render_level18_archive_index_report(index)

    assert "# Level 18 Archive Index Report" in markdown
    assert "## Artifact families" in markdown
    assert "## Path-only inventory" in markdown
    assert "## Review-only boundary" in markdown
    assert "## Expected validation commands" in markdown
    assert "## Next-level preconditions" in markdown
    assert "Path only: `True`" in markdown
    assert "Review only: `True`" in markdown
    assert "Content read: `False`" in markdown
    assert "Command executed: `False`" in markdown
    assert "Claim generated: `False`" in markdown
    validate_level18_archive_index_report(markdown)


def test_archive_index_report_writer(tmp_path) -> None:
    index = build_level18_archive_index()
    markdown = render_level18_archive_index_report(index)
    path = tmp_path / "level18-archive-index-report.md"

    write_level18_archive_index_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 18 Archive Index Report")
