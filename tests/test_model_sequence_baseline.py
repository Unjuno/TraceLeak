import json
from pathlib import Path

import pytest

from traceleak.model_sequence_baseline import (
    ModelSequenceBaselineError,
    evaluate_model_sequence_baselines,
    parse_labeled_model_sequence_counts,
    parse_labeled_model_sequences,
)


def sample_input() -> dict:
    return json.loads(
        Path("examples/synthetic/model_sequence_baseline_sample.json").read_text(encoding="utf-8")
    )


def test_parse_labeled_model_sequence_counts() -> None:
    examples = parse_labeled_model_sequence_counts(sample_input())
    assert len(examples) == 4
    assert examples[0].label == "1"
    assert examples[0].run_id == "synthetic_seq_000001"
    assert examples[0].token_counts["event_type=branch"] == 1.0


def test_parse_labeled_model_sequences_accepts_examples_format() -> None:
    data = {
        "examples": [
            {
                "run_id": "seq_1",
                "label": "x",
                "sequence": [
                    {
                        "event_token": "branch:p:f:n",
                        "source_token": "file.c:1:f:n",
                        "context_token": "p:f",
                        "event_type": "branch",
                        "phase": "p",
                    }
                ],
            },
            {
                "run_id": "seq_2",
                "label": "y",
                "sequence": [
                    {
                        "event_token": "loop:p:f:m",
                        "source_token": "file.c:2:f:m",
                        "context_token": "p:f",
                        "event_type": "loop",
                        "phase": "p",
                    }
                ],
            },
        ]
    }
    examples = parse_labeled_model_sequences(data)
    assert len(examples) == 2
    assert examples[0].label == "x"


def test_evaluate_model_sequence_baselines() -> None:
    result = evaluate_model_sequence_baselines(sample_input())
    assert result["result_type"] == "model_sequence_baseline"
    assert result["target"] == "synthetic-leak"
    assert result["view"] == "redacted"
    assert result["label_distribution"] == {"0": 2, "1": 2}
    assert result["baselines"]["leave_one_out_majority_accuracy"] == 0.0
    assert result["baselines"]["leave_one_out_nearest_neighbor_accuracy"] == 1.0


def test_evaluate_model_sequence_baselines_rejects_missing_records() -> None:
    with pytest.raises(ModelSequenceBaselineError):
        evaluate_model_sequence_baselines({"records": []})


def test_evaluate_model_sequence_baselines_rejects_missing_step_fields() -> None:
    data = {
        "examples": [
            {
                "run_id": "bad",
                "label": "x",
                "sequence": [{"event_token": "event"}],
            }
        ]
    }
    with pytest.raises(ModelSequenceBaselineError):
        evaluate_model_sequence_baselines(data)
