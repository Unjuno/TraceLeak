"""Baseline evaluation for variable/control-flow model sequences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from traceleak.baselines import (
    BaselineError,
    LabeledFeatureVector,
    label_distribution,
    leave_one_out_majority_accuracy,
    leave_one_out_nearest_neighbor_accuracy,
)
from traceleak.model_features import ModelSequence, sequence_token_counts


class ModelSequenceBaselineError(ValueError):
    """Raised when labeled model sequence baseline input is invalid."""


@dataclass(frozen=True)
class LabeledModelSequence:
    """A model sequence with one evaluation label."""

    label: str
    sequence: ModelSequence
    run_id: str | None = None
    metadata: dict[str, Any] | None = None


def labeled_sequence_to_feature_vector(example: LabeledModelSequence) -> LabeledFeatureVector:
    """Convert a labeled sequence into token-count features for lightweight baselines."""

    return LabeledFeatureVector(
        label=example.label,
        features=sequence_token_counts(example.sequence),
        run_id=example.run_id,
        metadata=example.metadata,
    )


def parse_labeled_model_sequences(data: dict[str, Any]) -> list[LabeledModelSequence]:
    """Parse labeled model sequences from a public-safe JSON object."""

    examples = data.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ModelSequenceBaselineError("examples must be a non-empty list")

    parsed: list[LabeledModelSequence] = []
    for index, item in enumerate(examples):
        if not isinstance(item, dict):
            raise ModelSequenceBaselineError(f"examples[{index}] must be an object")
        if "label" not in item:
            raise ModelSequenceBaselineError(f"examples[{index}] is missing label")
        sequence = item.get("sequence")
        if not isinstance(sequence, list) or not sequence:
            raise ModelSequenceBaselineError(f"examples[{index}] must contain a non-empty sequence")
        for step_index, step in enumerate(sequence):
            if not isinstance(step, dict):
                raise ModelSequenceBaselineError(
                    f"examples[{index}].sequence[{step_index}] must be an object"
                )
            _require_step_fields(step, example_index=index, step_index=step_index)
        parsed.append(
            LabeledModelSequence(
                label=str(item["label"]),
                sequence=sequence,
                run_id=item.get("run_id"),
                metadata=item.get("metadata"),
            )
        )
    return parsed


def evaluate_model_sequence_baselines(data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate majority and nearest-neighbor baselines over model sequence tokens."""

    sequences = parse_labeled_model_sequences(data)
    vectors = [labeled_sequence_to_feature_vector(sequence) for sequence in sequences]
    try:
        majority_accuracy = leave_one_out_majority_accuracy(vectors)
        nearest_neighbor_accuracy = leave_one_out_nearest_neighbor_accuracy(vectors)
    except BaselineError as exc:
        raise ModelSequenceBaselineError(str(exc)) from exc

    return {
        "result_type": "model_sequence_baseline",
        "target": data.get("target", "unknown"),
        "view": data.get("view", "unknown"),
        "label_name": data.get("label_name", "label"),
        "feature_source": "model_sequence_token_counts",
        "example_count": len(sequences),
        "label_distribution": label_distribution(vectors),
        "baselines": {
            "leave_one_out_majority_accuracy": majority_accuracy,
            "leave_one_out_nearest_neighbor_accuracy": nearest_neighbor_accuracy,
        },
        "notes": data.get("notes", []),
    }


def _require_step_fields(step: dict[str, Any], *, example_index: int, step_index: int) -> None:
    required = [
        "event_token",
        "source_token",
        "context_token",
        "event_type",
        "phase",
    ]
    for field in required:
        if field not in step:
            raise ModelSequenceBaselineError(
                f"examples[{example_index}].sequence[{step_index}] is missing {field}"
            )
