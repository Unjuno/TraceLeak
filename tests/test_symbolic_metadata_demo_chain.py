import json

import pytest

from traceleak.symbolic_metadata_demo_chain import (
    DEFAULT_OUTPUT_NAMES,
    SYMBOLIC_METADATA_DEMO_CHAIN_FORMAT,
    SymbolicMetadataDemoChainError,
    build_symbolic_metadata_demo_chain,
    validate_symbolic_metadata_demo_summary,
    write_symbolic_metadata_demo_chain,
)
from traceleak.symbolic_metadata_demo_report import (
    render_symbolic_metadata_demo_report,
    validate_symbolic_metadata_demo_report,
    write_symbolic_metadata_demo_report,
)


def test_symbolic_metadata_demo_chain_builds_end_to_end_outputs() -> None:
    artifacts = build_symbolic_metadata_demo_chain(epochs=20)
    summary = artifacts["demo_summary"]

    assert set(artifacts) == set(DEFAULT_OUTPUT_NAMES)
    assert summary["format"] == SYMBOLIC_METADATA_DEMO_CHAIN_FORMAT
    assert summary["phase"] == "P84"
    assert summary["record_count"] == 4
    assert summary["flags"]["metadata_only"] is True
    assert summary["flags"]["payload_free"] is True
    assert summary["flags"]["openssl_leakage_claim"] is False
    assert artifacts["baseline_result"]["result_type"] == "model_sequence_baseline"
    assert artifacts["nn_result"]["result_type"] == "model_sequence_nn"
    validate_symbolic_metadata_demo_summary(summary)


def test_symbolic_metadata_demo_chain_writes_outputs(tmp_path) -> None:
    artifacts = build_symbolic_metadata_demo_chain(epochs=20)
    paths = write_symbolic_metadata_demo_chain(output_dir=tmp_path / "symbolic", artifacts=artifacts)

    assert set(paths) == set(DEFAULT_OUTPUT_NAMES)
    for key, path in paths.items():
        assert path.exists(), key
        assert isinstance(json.loads(path.read_text(encoding="utf-8")), dict)


def test_symbolic_metadata_demo_report_renders_markdown() -> None:
    artifacts = build_symbolic_metadata_demo_chain(epochs=20)

    markdown = render_symbolic_metadata_demo_report(artifacts["demo_summary"])

    assert "# Symbolic Metadata Demo Report" in markdown
    assert "## Label distribution" in markdown
    assert "## Neural model" in markdown
    assert "not OpenSSL leakage evidence" in markdown
    validate_symbolic_metadata_demo_report(markdown)


def test_symbolic_metadata_demo_report_writes_markdown(tmp_path) -> None:
    artifacts = build_symbolic_metadata_demo_chain(epochs=20)
    markdown = render_symbolic_metadata_demo_report(artifacts["demo_summary"])
    path = tmp_path / "symbolic-demo-report.md"

    write_symbolic_metadata_demo_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# Symbolic Metadata Demo Report")


def test_symbolic_metadata_demo_chain_rejects_bad_epochs() -> None:
    with pytest.raises(SymbolicMetadataDemoChainError, match="epochs"):
        build_symbolic_metadata_demo_chain(epochs=0)
