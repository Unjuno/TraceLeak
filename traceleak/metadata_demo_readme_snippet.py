"""Command snippet helpers for local metadata demo outputs."""

from __future__ import annotations

from pathlib import Path

METADATA_DEMO_README_SNIPPET_PHASE = "P78"


class MetadataDemoReadmeSnippetError(ValueError):
    """Raised when a local demo command snippet is invalid."""


def render_metadata_demo_readme_snippet(*, output_dir: Path | str = "reports/local/openssl_metadata_demo") -> str:
    """Render a short copy/paste command block for local demo generation."""

    output_text = _safe_output_dir_text(output_dir)
    command = (
        "traceleak-run-openssl-metadata-demo-chain "
        f"--out-dir {output_text} "
        "--record-count 4 "
        "--epochs 20 "
        "--write-markdown-summary "
        "--include-ranking "
        "--write-metrics-json "
        "--write-metrics-csv "
        "--write-artifact-index-json "
        "--write-artifact-index-markdown"
    )
    markdown = "\n".join(
        [
            "# Metadata Demo Local Commands",
            "",
            f"- Phase: `{METADATA_DEMO_README_SNIPPET_PHASE}`",
            "- Scope: local demo outputs only",
            "",
            "```powershell",
            "cd C:\\Users\\junny\\Desktop\\traceLeak\\TraceLeak",
            command,
            "```",
            "",
            "Generated files should stay under `reports/local/`.",
            "",
        ]
    )
    validate_metadata_demo_readme_snippet(markdown)
    return markdown


def write_metadata_demo_readme_snippet(path: Path, markdown: str) -> None:
    """Write a local demo command snippet."""

    validate_metadata_demo_readme_snippet(markdown)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def validate_metadata_demo_readme_snippet(markdown: str) -> None:
    """Validate the local demo command snippet shape."""

    if not isinstance(markdown, str) or not markdown.endswith("\n"):
        raise MetadataDemoReadmeSnippetError("markdown must be a newline-terminated string")
    for required in [
        "# Metadata Demo Local Commands",
        f"- Phase: `{METADATA_DEMO_README_SNIPPET_PHASE}`",
        "```powershell",
        "traceleak-run-openssl-metadata-demo-chain",
        "--write-artifact-index-json",
        "--write-artifact-index-markdown",
        "Generated files should stay under `reports/local/`.",
    ]:
        if required not in markdown:
            raise MetadataDemoReadmeSnippetError(f"missing snippet text: {required}")


def _safe_output_dir_text(output_dir: Path | str) -> str:
    value = str(output_dir).replace("\\", "/")
    if not value or value.startswith("/") or ".." in Path(value).parts:
        raise MetadataDemoReadmeSnippetError("output_dir must be a non-empty relative path")
    if any(char.isspace() for char in value):
        raise MetadataDemoReadmeSnippetError("output_dir must not contain whitespace")
    return value
