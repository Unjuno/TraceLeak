"""Consumer-view adapters for DeepProgramSample records."""

from __future__ import annotations

from typing import Any

from traceleak.deep_program_dataset import validate_deep_program_sample

DEEP_SAMPLE_CONSUMER_VIEW_FORMAT = "traceleak.deep_sample_consumer_view.v1"


class DeepSampleConsumerError(ValueError):
    """Raised when a DeepProgramSample cannot be adapted for a consumer."""


def sample_for_consumer_mode(sample: dict[str, Any], consumer_mode: str) -> dict[str, Any]:
    """Return the model-facing subset for one consumer mode."""

    validate_deep_program_sample(sample)
    _require_supported_mode(sample, consumer_mode)
    if consumer_mode == "sequence":
        payload = {
            "program_events": sample["program_events"],
            "variable_state_sequence": sample["variable_state_sequence"],
        }
    elif consumer_mode == "graph":
        payload = {
            "dependency_graph": sample["dependency_graph"],
        }
    elif consumer_mode == "hybrid":
        payload = {
            "program_events": sample["program_events"],
            "variable_state_sequence": sample["variable_state_sequence"],
            "dependency_graph": sample["dependency_graph"],
        }
    else:
        raise DeepSampleConsumerError(f"unsupported consumer_mode: {consumer_mode}")
    return {
        "format": DEEP_SAMPLE_CONSUMER_VIEW_FORMAT,
        "sample_id": sample["sample_id"],
        "consumer_mode": consumer_mode,
        "inputs": payload,
        "feature_names": sample["feature_names"],
        "metadata": {
            "source_format": sample["format"],
            "input_keys": sorted(payload),
        },
    }


def samples_for_consumer_mode(samples: list[dict[str, Any]], consumer_mode: str) -> list[dict[str, Any]]:
    """Adapt multiple DeepProgramSample records for one consumer mode."""

    return [sample_for_consumer_mode(sample, consumer_mode) for sample in samples]


def _require_supported_mode(sample: dict[str, Any], consumer_mode: str) -> None:
    modes = sample["masks"]["consumer_modes"]
    if consumer_mode not in modes:
        raise DeepSampleConsumerError(f"sample does not support consumer_mode: {consumer_mode}")
