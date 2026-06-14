import json

from scripts import compare_demo_summaries as cli
from traceleak.openssl_metadata_demo_chain import (
    build_openssl_metadata_demo_chain,
    write_openssl_metadata_demo_chain,
)
from traceleak.symbolic_metadata_demo_chain import (
    build_symbolic_metadata_demo_chain,
    write_symbolic_metadata_demo_chain,
)


def write_inputs(tmp_path):
    metadata_dir = tmp_path / "metadata_demo"
    symbolic_dir = tmp_path / "symbolic_demo"
    write_openssl_metadata_demo_chain(
        output_dir=metadata_dir,
        artifacts=build_openssl_metadata_demo_chain(epochs=20),
    )
    write_symbolic_metadata_demo_chain(
        output_dir=symbolic_dir,
        artifacts=build_symbolic_metadata_demo_chain(epochs=20),
    )
    return metadata_dir / "demo-summary.json", symbolic_dir / "symbolic-demo-summary.json"


def test_compare_demo_summaries_cli_writes_json_and_markdown(tmp_path, monkeypatch) -> None:
    metadata_summary, symbolic_summary = write_inputs(tmp_path)
    out_path = tmp_path / "comparison.json"
    markdown_path = tmp_path / "comparison.md"
    monkeypatch.setattr(
        "sys.argv",
        [
            "compare_demo_summaries",
            "--metadata-summary",
            str(metadata_summary),
            "--symbolic-summary",
            str(symbolic_summary),
            "--out",
            str(out_path),
            "--markdown-out",
            str(markdown_path),
        ],
    )

    assert cli.main() == 0
    comparison = json.loads(out_path.read_text(encoding="utf-8"))
    assert comparison["format"] == "traceleak.demo_summary_comparison.v1"
    assert comparison["phase"] == "P87"
    assert markdown_path.read_text(encoding="utf-8").startswith("# Demo Summary Comparison")


def test_compare_demo_summaries_cli_rejects_missing_input(tmp_path, monkeypatch) -> None:
    metadata_summary, _symbolic_summary = write_inputs(tmp_path)
    out_path = tmp_path / "comparison.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "compare_demo_summaries",
            "--metadata-summary",
            str(metadata_summary),
            "--symbolic-summary",
            str(tmp_path / "missing.json"),
            "--out",
            str(out_path),
        ],
    )

    assert cli.main() == 1
    assert not out_path.exists()
