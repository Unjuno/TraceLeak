# ruff: noqa: I001

import json
from pathlib import Path

from traceleak.model_sequence_comparison import compare_model_sequence_nn_to_baseline
from traceleak.model_sequence_comparison_reporting import (
    attribution_status,
    control_summary_dict,
    evidence_status,
    expected_attribution_matches,
    model_sequence_comparison_report_dict,
    model_sequence_comparison_report_markdown,
)


RATIO_TOKENS = {
    "event_token=loop:candidate_balance:synthetic_keygen:refine_round",
    "event_token=loop:candidate_balance:synthetic_keygen:accept_round",
}
EXPECTED_TOKEN = "event_token=loop:candidate_balance:synthetic_keygen:refine_round"
MISSING_EXPECTED_TOKEN = "event_token=branch:candidate_balance:synthetic_keygen:missing_branch"


def comparison_result() -> dict:
    return {
        "result_type": "model_sequence_nn_vs_baseline",
        "target": "synthetic-count-pattern",
        "view": "redacted",
        "label_name": "secret_bucket",
        "example_count": 16,
        "baseline": {
            "leave_one_out_majority_accuracy": 0.0,
            "leave_one_out_nearest_neighbor_accuracy": 0.25,
        },
        "neural": {
            "model_name": "sparse-softmax-model-sequence-nn",
            "backend": "python-standard-library",
            "leave_one_out_accuracy": 1.0,
            "DeltaH": 1.0,
            "top_attributions": [
                {
                    "group_id": EXPECTED_TOKEN,
                    "group_type": "model_sequence_token",
                    "score": 0.75,
                    "evidence": ["sparse_softmax_weight_separation"],
                }
            ],
        },
        "delta": {"accuracy_vs_nearest_neighbor": 0.75},
        "interpretation": "neural_better",
        "notes": ["sample note"],
    }


def control_result(target: str, neural_accuracy: float) -> dict:
    result = comparison_result()
    result["target"] = target
    result["label_name"] = f"{target}_label"
    result["neural"] = dict(result["neural"])
    result["neural"]["leave_one_out_accuracy"] = neural_accuracy
    result["neural"]["DeltaH"] = 0.0
    result["delta"] = {"accuracy_vs_nearest_neighbor": neural_accuracy - 0.25}
    result["interpretation"] = "baseline_better"
    return result


def test_model_sequence_comparison_report_dict() -> None:
    report = model_sequence_comparison_report_dict(comparison_result())

    assert report["report_type"] == "model_sequence_nn_comparison_report"
    assert report["baseline_accuracy"] == 0.25
    assert report["neural_accuracy"] == 1.0
    assert report["evidence_status"] == "controls_missing"
    assert report["attribution_status"] == "expected_attributions_not_declared"
    assert report["control_warning"] == "not_a_control_result"
    assert report["top_attributions"]


def test_model_sequence_comparison_report_dict_with_controls() -> None:
    controls = [
        control_result("synthetic-count-pattern-control-001", 0.0),
        control_result("synthetic-count-pattern-control-002", 0.25),
    ]
    report = model_sequence_comparison_report_dict(
        comparison_result(),
        controls=controls,
        expected_attribution_tokens=[EXPECTED_TOKEN],
    )

    assert report["control_summary"]["control_count"] == 2
    assert report["control_summary"]["max_neural_accuracy"] == 0.25
    assert report["control_summary"]["status"] == "control_pass"
    assert report["evidence_status"] == "candidate_signal_control_checked"
    assert report["attribution_status"] == "expected_attribution_observed"
    assert report["attribution_matches"] == [EXPECTED_TOKEN]


def test_control_summary_rejects_high_control_accuracy() -> None:
    summary = control_summary_dict([control_result("synthetic-count-pattern-control-001", 0.75)])

    assert summary["status"] == "control_attention"


def test_evidence_status_requires_neural_gain_and_controls() -> None:
    assert evidence_status("similar", None) == "no_neural_advantage"
    assert evidence_status("neural_better", None) == "controls_missing"
    assert (
        evidence_status("neural_better", {"status": "control_attention"})
        == "control_attention_required"
    )
    assert (
        evidence_status("neural_better", {"status": "control_pass"})
        == "candidate_signal_control_checked"
    )


def test_attribution_status_requires_expected_token_match() -> None:
    top_attributions = comparison_result()["neural"]["top_attributions"]

    assert attribution_status(top_attributions, []) == "expected_attributions_not_declared"
    assert attribution_status([], [EXPECTED_TOKEN]) == "attributions_missing"
    assert attribution_status(top_attributions, [EXPECTED_TOKEN]) == "expected_attribution_observed"
    assert (
        attribution_status(top_attributions, [MISSING_EXPECTED_TOKEN])
        == "expected_attribution_missing"
    )
    assert expected_attribution_matches(top_attributions, [EXPECTED_TOKEN]) == [EXPECTED_TOKEN]


def test_model_sequence_comparison_report_markdown() -> None:
    report = model_sequence_comparison_report_dict(
        comparison_result(),
        controls=[control_result("synthetic-count-pattern-control-001", 0.0)],
        expected_attribution_tokens=[EXPECTED_TOKEN],
    )
    markdown = model_sequence_comparison_report_markdown(report)

    assert "TraceLeak Model Sequence NN Comparison Report" in markdown
    assert "Nearest-neighbor baseline" in markdown
    assert "Sparse-softmax NN" in markdown
    assert "Top NN Attributions" in markdown
    assert "Control Summary" in markdown
    assert "Expected Attribution Tokens" in markdown
    assert "Attribution Matches" in markdown
    assert "neural_better" in markdown
    assert "candidate_signal_control_checked" in markdown
    assert "expected_attribution_observed" in markdown


def test_count_pattern_sample_favors_count_learning_over_jaccard_presence() -> None:
    data = json.loads(
        Path("examples/synthetic/model_sequence_nn_count_pattern_sample.json").read_text(
            encoding="utf-8"
        )
    )
    result = compare_model_sequence_nn_to_baseline(data, epochs=80, learning_rate=0.8)

    attribution_tokens = {item["group_id"] for item in result["neural"]["top_attributions"]}
    assert result["example_count"] == 16
    assert result["baseline"]["leave_one_out_nearest_neighbor_accuracy"] < result["neural"][
        "leave_one_out_accuracy"
    ]
    assert result["interpretation"] == "neural_better"
    assert attribution_tokens >= RATIO_TOKENS
