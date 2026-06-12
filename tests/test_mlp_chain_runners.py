import json
from pathlib import Path

from scripts import run_mlp_expected_check, run_mlp_report_chain


def test_run_mlp_report_chain_writes_expected_artifacts(tmp_path: Path) -> None:
    assert run_mlp_report_chain.main(["--out-dir", str(tmp_path)]) == 0

    report_path = tmp_path / "toy_rsa_like_model_sequence_mlp_comparison_report.json"
    markdown_path = tmp_path / "toy_rsa_like_model_sequence_mlp_comparison.md"
    assert report_path.exists()
    assert markdown_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert report["validation_scope"] == "toy_local_validation"
    assert report["actual_trace_derived"] is False
    assert report["neural_model_name"] == "mlp-model-sequence-nn"
    assert report["neural_architecture"] == "one-hidden-layer-tanh-softmax"
    assert report["evidence_status"] == "candidate_signal_control_checked"
    assert report["attribution_status"] == "expected_attribution_observed"
    assert report["control_summary"]["status"] == "control_pass"
    assert "Toy/local validation only" in markdown
    assert "actual OpenSSL traces" in markdown
    assert "| mlp-model-sequence-nn | 1 |" in markdown


def test_run_mlp_expected_check_writes_expected_artifacts(tmp_path: Path) -> None:
    assert run_mlp_expected_check.main(["--out-dir", str(tmp_path)]) == 0

    report_path = tmp_path / "toy_rsa_like_model_sequence_mlp_expected_check.json"
    markdown_path = tmp_path / "toy_rsa_like_model_sequence_mlp_expected_check.md"
    assert report_path.exists()
    assert markdown_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert report["validation_scope"] == "toy_local_validation"
    assert report["actual_trace_derived"] is False
    assert report["status"] == "expected_token_sensitive"
    assert report["nn_accuracy_drop"] >= 0.25
    assert report["expected_tokens"] == run_mlp_expected_check.EXPECTED
    assert "Status: `expected_token_sensitive`" in markdown
    assert "Validation scope: `toy_local_validation`" in markdown
    assert "Actual trace derived: `false`" in markdown
