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


@dataclass(frozen=True)
class LabeledModelSequenceCounts:
    """Token-count features derived from one labeled model sequence."""

    label: str
    token_counts: dict[str, float]
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


def labeled_counts_to_feature_vector(example: LabeledModelSequenceCounts) -> LabeledFeatureVector:
    """Convert labeled sequence token counts into a baseline feature vector."""

    return LabeledFeatureVector(
        label=example.label,
        features=example.token_counts,
        run_id=example.run_id,
        metadata=example.metadata,
    )


def parse_labeled_model_sequences(data: dict[str, Any]) -> list[LabeledModelSequence]:
    """Parse labeled model sequences from an `examples` JSON object."""

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
        _validate_sequence(sequence, record_name=f"examples[{index}]")
        parsed.append(
            LabeledModelSequence(
                label=str(item["label"]),
                sequence=sequence,
                run_id=item.get("run_id"),
                metadata=item.get("metadata"),
            )
        )
    return parsed


def parse_labeled_model_sequence_counts(data: dict[str, Any]) -> list[LabeledModelSequenceCounts]:
    """Parse labeled model sequence token counts from a `records` JSON object."""

    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ModelSequenceBaselineError("records must be a non-empty list")

    parsed: list[LabeledModelSequenceCounts] = []
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise ModelSequenceBaselineError(f"records[{index}] must be an object")
        if "label" not in item:
            raise ModelSequenceBaselineError(f"records[{index}] is missing label")
        counts = item.get("token_counts")
        if not isinstance(counts, dict) or not counts:
            raise ModelSequenceBaselineError(f"records[{index}] must contain non-empty token_counts")
        parsed.append(
            LabeledModelSequenceCounts(
                label=str(item["label"]),
                token_counts={str(name): float(value) for name, value in counts.items()},
                run_id=item.get("run_id"),
                metadata={
                    "target": item.get("target"),
                    "view": item.get("view"),
                    "target_version": item.get("target_version"),
                },
            )
        )
    return parsed


def evaluate_model_sequence_baselines(data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate majority and nearest-neighbor baselines over model sequence tokens."""

    if "records" in data:
        count_examples = parse_labeled_model_sequence_counts(data)
        vectors = [labeled_counts_to_feature_vector(example) for example in count_examples]
        target = _common_metadata_value(vectors, "target")
        view = _common_metadata_value(vectors, "view")
        example_count = len(count_examples)
        notes = data.get("notes") or [
            "Baseline over variable/control-flow model sequence token counts.",
            "This is not neural training; it is a lightweight sanity check before local NN work.",
        ]
    else:
        sequence_examples = parse_labeled_model_sequences(data)
        vectors = [labeled_sequence_to_feature_vector(example) for example in sequence_examples]
        target = data.get("target", "unknown")
        view = data.get("view", "unknown")
        example_count = len(sequence_examples)
        notes = data.get("notes", [])

    try:
        majority_accuracy = leave_one_out_majority_accuracy(vectors)
        nearest_neighbor_accuracy = leave_one_out_nearest_neighbor_accuracy(vectors)
    except BaselineError as exc:
        raise ModelSequenceBaselineError(str(exc)) from exc

    return {
        "result_type": "model_sequence_baseline",
        "input_format": data.get("format", "unknown"),
        "target": target,
        "view": view,
        "label_name": data.get("label_name", "label"),
        "feature_source": "model_sequence_token_counts",
        "example_count": example_count,
        "label_distribution": label_distribution(vectors),
        "baselines": {
            "leave_one_out_majority_accuracy": majority_accuracy,
            "leave_one_out_nearest_neighbor_accuracy": nearest_neighbor_accuracy,
        },
        "notes": notes,
    }


def _validate_sequence(sequence: ModelSequence, *, record_name: str) -> None:
    for step_index, step in enumerate(sequence):
        if not isinstance(step, dict):
            raise ModelSequenceBaselineError(f"{record_name}.sequence[{step_index}] must be an object")
        _require_step_fields(step, record_name=record_name, step_index=step_index)


def _require_step_fields(step: dict[str, Any], *, record_name: str, step_index: int) -> None:
    required = [
        "event_token",
        "source_token",
        "context_token",
        "event_type",
        "phase",
    ]
    for field in required:
        if field not in step:
            raise ModelSequenceBaselineError(f"{record_name}.sequence[{step_index}] is missing {field}")


def _common_metadata_value(examples: list[LabeledFeatureVector], key: str) -> str:
    values = {str(example.metadata.get(key)) for example in examples if example.metadata and key in example.metadata}
    if len(values) == 1:
        return next(iter(values))
    return "mixed"
