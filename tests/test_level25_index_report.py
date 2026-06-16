from traceleak.level25_index import (
    build_level25_index,
    render_level25_index_report,
    validate_level25_index_report,
    write_level25_index_report,
)


def test_level25_index_report_sections() -> None:
    index = build_level25_index()

    markdown = render_level25_index_report(index)

    assert "# Level 25 Index Report" in markdown
    assert "## Output paths" in markdown
    assert "## Expected validation commands" in markdown
    validate_level25_index_report(markdown)


def test_level25_index_report_writer(tmp_path) -> None:
    index = build_level25_index()
    markdown = render_level25_index_report(index)
    path = tmp_path / "level25-index-report.md"

    write_level25_index_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Level 25 Index Report")
