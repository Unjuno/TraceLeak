from traceleak.model_sequence_cross_report import (
    model_sequence_cross_report_dict,
    model_sequence_cross_report_markdown,
)


def comparison(target: str) -> dict:
    return {
        "result_type": "model_sequence_nn_vs_baseline",
        "target": target,
        "view": "redacted",
        "label_name": "secret_bucket",
        "example_count": 16,
        "baseline": {
            "leave_one_out_majority_accuracy": 0.0,
            "leave_one_out_nearest_neighbor_accuracy": 0.4375,
        },
        "neural": {
            "model_name": "sparse-softmax-model-sequence-nn",
            "backend": "python-standard-library",
            "leave_one_out_accuracy": 1.0,
            "DeltaH": 1.0,
            "top_attributions": [
                {
                    "group_id": f"event_token=loop:{target}:ratio_a",
                    "group_type": "model_sequence_token",
                    "score": 10.0,
                    "evidence": ["sparse_softmax_weight_separation"],
                },
                {
                    "group_id": f"event_token=loop:{target}:ratio_b",
                    "group_type": "model_sequence_token",
                    "score": 9.0,
                    "evidence": ["sparse_softmax_weight_separation"],
                },
            ],
        },
        "delta": {"accuracy_vs_nearest_neighbor": 0.5625},
        "interpretation": "neural_better",
        "notes": ["sample note"],
    }


def control(target: str) -> dict:
    result = comparison(target)
    result["target"] = f"{target}-control"
    result["label_name"] = "control_bucket"
    result["neural"] = dict(result["neural"])
    result["neural"]["leave_one_out_accuracy"] = 0.0
    result["neural"]["DeltaH"] = 0.0
    result["delta"] = {"accuracy_vs_nearest_neighbor": -0.4375}
    result["interpretation"] = "baseline_better"
    return result


def test_model_sequence_cross_report_dict() -> None:
    report = model_sequence_cross_report_dict(
        [
            {
                "name": "synthetic",
                "comparison": comparison("synthetic-count-pattern"),
                "controls": [control("synthetic-count-pattern")],
            },
            {
                "name": "toy-rsa-like",
                "comparison": comparison("toy-rsa-like-count-pattern"),
                "controls": [control("toy-rsa-like-count-pattern")],
            },
        ]
    )

    assert report["report_type"] == "model_sequence_cross_report"
    assert report["entry_count"] == 2
    assert report["rows"][0]["control_status"] == "control_pass"
    assert report["rows"][1]["delta_accuracy"] == 0.5625


def test_model_sequence_cross_report_markdown() -> None:
    report = model_sequence_cross_report_dict(
        [
            {
                "name": "synthetic",
                "comparison": comparison("synthetic-count-pattern"),
                "controls": [control("synthetic-count-pattern")],
            },
            {
                "name": "toy-rsa-like",
                "comparison": comparison("toy-rsa-like-count-pattern"),
                "controls": [control("toy-rsa-like-count-pattern")],
            },
        ]
    )
    markdown = model_sequence_cross_report_markdown(report)

    assert "TraceLeak Model Sequence Cross Report" in markdown
    assert "synthetic-count-pattern" in markdown
    assert "toy-rsa-like-count-pattern" in markdown
    assert "Attribution Alignment" in markdown
    assert "control_pass" in markdown
