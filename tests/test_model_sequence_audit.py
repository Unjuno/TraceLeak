from traceleak.model_sequence_audit import (
    ablate_model_sequence_sample,
    ablation_report_markdown,
    audit_report_markdown,
    label_leakage_audit,
    model_sequence_ablation_report,
    top_attribution_ablation_summary,
)


def sample() -> dict:
    return {
        "format": "traceleak.model_sequence.v1",
        "target": "toy-audit",
        "view": "redacted",
        "label_name": "prime_attempt_bucket",
        "include_counts": True,
        "records": [
            {
                "run_id": "r1",
                "target": "toy-audit",
                "view": "redacted",
                "label": "low",
                "token_counts": {
                    "event_token=loop:prime_candidate:attempt_round": 1,
                    "source_token=target.py:10:keygen:attempt_round": 1,
                    "context_token=keygen:attempt": 1,
                    "event_type=loop": 1,
                    "phase=keygen": 1,
                    "redacted_value=value_redacted.bucket=small": 1,
                },
            },
            {
                "run_id": "r2",
                "target": "toy-audit",
                "view": "redacted",
                "label": "low",
                "token_counts": {
                    "event_token=loop:prime_candidate:attempt_round": 1,
                    "source_token=target.py:10:keygen:attempt_round": 1,
                    "context_token=keygen:attempt": 1,
                    "event_type=loop": 1,
                    "phase=keygen": 1,
                    "redacted_value=value_redacted.bucket=small": 1,
                },
            },
            {
                "run_id": "r3",
                "target": "toy-audit",
                "view": "redacted",
                "label": "high",
                "token_counts": {
                    "event_token=loop:prime_candidate:attempt_round": 4,
                    "source_token=target.py:10:keygen:attempt_round": 4,
                    "context_token=keygen:attempt": 4,
                    "event_type=loop": 4,
                    "phase=keygen": 4,
                    "redacted_value=value_redacted.bucket=large": 1,
                },
            },
            {
                "run_id": "r4",
                "target": "toy-audit",
                "view": "redacted",
                "label": "high",
                "token_counts": {
                    "event_token=loop:prime_candidate:attempt_round": 4,
                    "source_token=target.py:10:keygen:attempt_round": 4,
                    "context_token=keygen:attempt": 4,
                    "event_type=loop": 4,
                    "phase=keygen": 4,
                    "redacted_value=value_redacted.bucket=large": 1,
                },
            },
        ],
    }


def test_label_leakage_audit_flags_overlap() -> None:
    report = label_leakage_audit(sample())
    markdown = audit_report_markdown(report)

    assert report["report_type"] == "model_sequence_label_leakage_audit"
    assert report["risk_level"] == "high"
    assert report["risky_token_count"] > 0
    assert "prime_candidate" in markdown


def test_ablate_model_sequence_sample_drop_redacted_value() -> None:
    ablated = ablate_model_sequence_sample(sample(), mode="drop_redacted_value")

    assert all(
        not token.startswith("redacted_value=")
        for record in ablated["records"]
        for token in record["token_counts"]
    )


def test_model_sequence_ablation_report() -> None:
    report = model_sequence_ablation_report(sample(), epochs=20, learning_rate=0.8, top_drop_k=1)
    markdown = ablation_report_markdown(report)

    assert report["report_type"] == "model_sequence_ablation_report"
    assert report["original"]["result_type"] == "model_sequence_nn_vs_baseline"
    assert {row["name"] for row in report["ablations"]} >= {
        "drop_redacted_value",
        "drop_source_token",
        "drop_context_token",
        "event_type_phase_only",
        "drop_top_attributions",
    }
    assert report["top_attribution_ablation"]["status"] in {
        "baseline_dominates",
        "top_attribution_sensitive",
        "top_attribution_stable",
    }
    assert report["top_attribution_ablation"]["dropped_tokens"]
    assert "TraceLeak Model Sequence Ablation Report" in markdown
    assert "Top attribution ablation status" in markdown
    assert "Top Attribution Ablation" in markdown


def test_top_attribution_ablation_summary_handles_missing_drop_row() -> None:
    original = {
        "neural": {"leave_one_out_accuracy": 1.0},
        "baseline": {"leave_one_out_nearest_neighbor_accuracy": 0.25},
    }

    summary = top_attribution_ablation_summary(original, [])

    assert summary["status"] == "not_run"
    assert summary["nn_accuracy_drop"] == 0.0
    assert summary["dropped_tokens"] == []
