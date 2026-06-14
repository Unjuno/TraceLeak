import pytest

from traceleak.metadata_demo_readme_snippet import (
    METADATA_DEMO_README_SNIPPET_PHASE,
    MetadataDemoReadmeSnippetError,
    render_metadata_demo_readme_snippet,
    validate_metadata_demo_readme_snippet,
    write_metadata_demo_readme_snippet,
)


def test_metadata_demo_readme_snippet_renders_command_block() -> None:
    markdown = render_metadata_demo_readme_snippet()

    assert "# Metadata Demo Local Commands" in markdown
    assert f"- Phase: `{METADATA_DEMO_README_SNIPPET_PHASE}`" in markdown
    assert "traceleak-run-openssl-metadata-demo-chain" in markdown
    assert "--write-artifact-index-json" in markdown
    assert "--write-command-snippet" in markdown
    assert markdown.endswith("\n")
    validate_metadata_demo_readme_snippet(markdown)


def test_metadata_demo_readme_snippet_uses_custom_output_dir() -> None:
    markdown = render_metadata_demo_readme_snippet(output_dir="reports/local/custom_demo")

    assert "--out-dir reports/local/custom_demo" in markdown


def test_metadata_demo_readme_snippet_allows_absolute_temp_dir(tmp_path) -> None:
    markdown = render_metadata_demo_readme_snippet(output_dir=tmp_path)

    assert f"--out-dir {tmp_path.as_posix()}" in markdown


def test_metadata_demo_readme_snippet_writes_file(tmp_path) -> None:
    path = tmp_path / "demo-commands.md"
    markdown = render_metadata_demo_readme_snippet()

    write_metadata_demo_readme_snippet(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Metadata Demo Local Commands")


def test_metadata_demo_readme_snippet_rejects_unsafe_output_dir() -> None:
    with pytest.raises(MetadataDemoReadmeSnippetError, match="parent traversal"):
        render_metadata_demo_readme_snippet(output_dir="../bad")
