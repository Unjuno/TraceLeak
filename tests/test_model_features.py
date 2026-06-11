import json
from pathlib import Path

import pytest

from traceleak.model_features import (
    ModelFeatureError,
    event_token,
    model_sequence_vocabulary,
    redacted_value_tokens,
    sequence_token_counts,
    source_token,
    trace_to_model_sequence,
)


def sample_run() -> dict:
    return {
        "run_id": "synthetic_000001",
        "target": "synthetic-leak",
        "target_version": "v0",
        "view": "redacted",
        "events": [
            {
                "event_type": "phase",
                "file": "examples/synthetic/target.c",
                "function": "synthetic_keygen",
                "line": 10,
                "name": "keygen_start",
                "phase": "keygen_start",
                "step": 1,
            },
            {
                "event_type": "branch",
                "file": "examples/synthetic/target.c",
                "function": "synthetic_keygen",
                "line": 21,
                "name": "secret_dependent_branch",
                "phase": "synthetic_leak",
                "step": 2,
                "value_redacted": {"branch_taken": True},
            },
            {
                "event_type": "loop",
                "file": "examples/synthetic/target.c",
                "function": "synthetic_keygen",
                "line": 22,
                "name": "dummy_loop_count",
                "phase": "synthetic_leak",
                "step": 3,
                "value_redacted": {"bucket": "64-127", "bit_length": 7},
            },
        ],
    }


def test_event_and_source_tokens() -> None:
    event = sample_run()["events"][1]
    assert event_token(event) == "branch:synthetic_leak:synthetic_keygen:secret_dependent_branch"
    assert (
        source_token(event)
        == "examples/synthetic/target.c:21:synthetic_keygen:secret_dependent_branch"
    )


def test_redacted_value_tokens() -> None:
    event = sample_run()["events"][2]
    tokens = redacted_value_tokens(event)
    assert "value_redacted.bucket=64-127" in tokens
    assert "value_redacted.bit_length=7" in tokens


def test_trace_to_model_sequence_preserves_program_order() -> None:
    run = sample_run()
    run["events"] = list(reversed(run["events"]))
    sequence = trace_to_model_sequence(run)
    assert [step["step"] for step in sequence] == [1, 2, 3]
    assert sequence[1]["event_type"] == "branch"
    assert sequence[1]["redacted_value_tokens"] == ["value_redacted.branch_taken=true"]


def test_trace_to_model_sequence_rejects_raw_by_default() -> None:
    run = sample_run()
    run["view"] = "raw"
    with pytest.raises(ModelFeatureError):
        trace_to_model_sequence(run)


def test_sequence_token_counts() -> None:
    sequence = trace_to_model_sequence(sample_run())
    counts = sequence_token_counts(sequence)
    assert counts["event_type=branch"] == 1.0
    assert counts["phase=synthetic_leak"] == 2.0
    assert counts["redacted_value=value_redacted.branch_taken=true"] == 1.0


def test_model_sequence_vocabulary() -> None:
    sequence = trace_to_model_sequence(sample_run())
    vocab = model_sequence_vocabulary([sequence])
    assert "branch:synthetic_leak:synthetic_keygen:secret_dependent_branch" in vocab
    assert "value_redacted.branch_taken=true" in vocab


def test_model_sequence_sample_matches_generated_sequence() -> None:
    expected = json.loads(
        Path("examples/synthetic/model_sequence_sample.json").read_text(encoding="utf-8")
    )
    sequence = trace_to_model_sequence(sample_run())
    assert expected["sequence"] == sequence
