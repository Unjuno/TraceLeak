"""Deep Program Dataset Contract v1.

This module bundles ProgramEvent, VariableStateRecord, and DependencyGraph
records into a single public-safe sample contract for sequence, graph, and
hybrid model consumers.  It validates labels separately from model-input
structures so supervised experiments can keep lab-only labels without leaking
those labels into public model features.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from traceleak.dependency_graph_schema import validate_dependency_graph
from traceleak.program_event_schema import FORBIDDEN_PUBLIC_FIELD_KEYS, validate_program_events
from traceleak.variable_state_sequence import validate_variable_state_sequence

DEEP_PROGRAM_DATASET_FORMAT = "traceleak.deep_program_dataset.v1"

ALLOWED_CONSUMER_MODES: set[str] = {
    "graph",
    "hybrid",
    "sequence",
}

REQUIRED_SAMPLE_FIELDS: tuple[str, ...] = (
    "sample_id",
    "format",
    "program_events",
    "variable_state_sequence",
    "dependency_graph",
    "labels",
    "masks",
    "feature_names",
    "metadata",
)

REQUIRED_MASK_FIELDS: tuple[str, ...] = (
    "consumer_modes",
    "use_program_events",
    "use_variable_state_sequence",
    "use_dependency_graph",
)

REQUIRED_FEATURE_NAME_FIELDS: tuple[str, ...] = (
    "program_event_features",
    "variable_state_features",
    "graph_node_features",
    "graph_edge_features",
)

DEFAULT_FEATURE_NAMES: dict[str, list[str]] = {
    "program_event_features": [
        "time_step",
        "event_type",
        "operation",
        "function",
        "value_class",
        "dependency_tags",
        "control_context",
    ],
    "variable_state_features": [
        "time_step",
        "variable_id",
        "scope",
        "state_class",
        "value_bucket",
        "source_event_id",
        "depends_on",
        "taint_class",
        "is_secret_derived",
    ],
    "graph_node_features": [
        "node_type",
        "label",
        "time_step",
        "metadata.derivation_method",
    ],
    "graph_edge_features": [
        "edge_type",
        "source_node_id",
        "target_node_id",
        "time_step",
        "metadata.derivation_method",
        "metadata.confidence",
    ],
}


class DeepProgramDatasetError(ValueError):
    """Raised when a Deep Program Dataset sample is invalid."""


@dataclass(frozen=True)
class DeepProgramSample:
    """Single model-ready program sample with sequence, state, and graph views."""

    sample_id: str
    program_events: list[dict[str, Any]]
    variable_state_sequence: list[dict[str, Any]]
    dependency_graph: dict[str, Any]
    labels: dict[str, Any]
    masks: dict[str, Any]
    feature_names: dict[str, list[str]]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic dictionary representation."""

        return {
            "sample_id": self.sample_id,
            "format": DEEP_PROGRAM_DATASET_FORMAT,
            "program_events": [dict(event) for event in self.program_events],
            "variable_state_sequence": [dict(record) for record in self.variable_state_sequence],
            "dependency_graph": dict(self.dependency_graph),
            "labels": dict(self.labels),
            "masks": dict(self.masks),
            "feature_names": {key: list(value) for key, value in self.feature_names.items()},
            "metadata": dict(self.metadata),
        }


def deep_program_sample_from_dict(
    data: dict[str, Any], *, public_safe: bool = True
) -> DeepProgramSample:
    """Validate and convert a dictionary into a DeepProgramSample."""

    validate_deep_program_sample(data, public_safe=public_safe)
    return DeepProgramSample(
        sample_id=data["sample_id"],
        program_events=[dict(event) for event in data["program_events"]],
        variable_state_sequence=[dict(record) for record in data["variable_state_sequence"]],
        dependency_graph=dict(data["dependency_graph"]),
        labels=dict(data["labels"]),
        masks=dict(data["masks"]),
        feature_names={key: list(value) for key, value in data["feature_names"].items()},
        metadata=dict(data["metadata"]),
    )


def validate_deep_program_sample(sample: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate one Deep Program Dataset v1 sample."""

    if not isinstance(sample, dict):
        raise DeepProgramDatasetError("deep program sample must be an object")
    for field_name in REQUIRED_SAMPLE_FIELDS:
        if field_name not in sample:
            raise DeepProgramDatasetError(f"missing required deep program sample field: {field_name}")

    _require_non_empty_string(sample["sample_id"], "sample_id")
    if sample["format"] != DEEP_PROGRAM_DATASET_FORMAT:
        raise DeepProgramDatasetError(
            f"invalid deep program sample format: {sample['format']!r}; expected: {DEEP_PROGRAM_DATASET_FORMAT}"
        )

    validate_program_events(_require_non_empty_list(sample["program_events"], "program_events"))
    validate_variable_state_sequence(
        _require_non_empty_list(sample["variable_state_sequence"], "variable_state_sequence")
    )
    validate_dependency_graph(_require_object(sample["dependency_graph"], "dependency_graph"))
    _validate_labels(sample["labels"], public_safe=public_safe)
    _validate_masks(sample["masks"])
    _validate_feature_names(sample["feature_names"])
    _require_object(sample["metadata"], "metadata")

    if public_safe:
        _reject_forbidden_public_fields(sample, "sample")


def deep_program_sample_from_components(
    *,
    sample_id: str,
    program_events: list[dict[str, Any]],
    variable_state_sequence: list[dict[str, Any]],
    dependency_graph: dict[str, Any],
    labels: dict[str, Any],
    consumer_modes: list[str] | tuple[str, ...] = ("sequence", "graph", "hybrid"),
    feature_names: dict[str, list[str]] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble one validated Deep Program Dataset sample from schema components."""

    _require_non_empty_string(sample_id, "sample_id")
    masks = masks_for_consumer_modes(list(consumer_modes))
    sample = {
        "sample_id": sample_id,
        "format": DEEP_PROGRAM_DATASET_FORMAT,
        "program_events": [dict(event) for event in program_events],
        "variable_state_sequence": [dict(record) for record in variable_state_sequence],
        "dependency_graph": dict(dependency_graph),
        "labels": dict(labels),
        "masks": masks,
        "feature_names": _feature_names_or_default(feature_names),
        "metadata": {
            "dataset_kind": "deep_program_dataset_sample",
            "claim_scope": "representation_only_not_leakage_proof",
            "supports_sequence_model": "sequence" in masks["consumer_modes"],
            "supports_graph_model": "graph" in masks["consumer_modes"],
            "supports_hybrid_model": "hybrid" in masks["consumer_modes"],
            **(metadata or {}),
        },
    }
    validate_deep_program_sample(sample)
    return sample


def masks_for_consumer_modes(consumer_modes: list[str] | tuple[str, ...]) -> dict[str, Any]:
    """Return model-consumer masks for sequence, graph, and hybrid consumers."""

    if not isinstance(consumer_modes, list | tuple) or not consumer_modes:
        raise DeepProgramDatasetError("consumer_modes must be a non-empty list")
    normalized = sorted({str(mode) for mode in consumer_modes})
    for mode in normalized:
        if mode not in ALLOWED_CONSUMER_MODES:
            raise DeepProgramDatasetError(_allowed_error("consumer_mode", mode, ALLOWED_CONSUMER_MODES))
    return {
        "consumer_modes": normalized,
        "use_program_events": bool({"sequence", "hybrid"} & set(normalized)),
        "use_variable_state_sequence": bool({"sequence", "hybrid"} & set(normalized)),
        "use_dependency_graph": bool({"graph", "hybrid"} & set(normalized)),
    }


def _validate_labels(labels: Any, *, public_safe: bool) -> None:
    labels_obj = _require_object(labels, "labels")
    if "training_target" not in labels_obj:
        raise DeepProgramDatasetError("labels.training_target is required")
    if "lab_only" not in labels_obj or not isinstance(labels_obj["lab_only"], bool):
        raise DeepProgramDatasetError("labels.lab_only must be a boolean")
    public_model_input = labels_obj.get("public_model_input", False)
    if not isinstance(public_model_input, bool):
        raise DeepProgramDatasetError("labels.public_model_input must be a boolean when present")
    if public_safe and public_model_input:
        raise DeepProgramDatasetError("lab labels must not be marked as public model input")
    if public_safe:
        _reject_forbidden_public_fields(labels_obj, "labels")


def _validate_masks(masks: Any) -> None:
    masks_obj = _require_object(masks, "masks")
    for field_name in REQUIRED_MASK_FIELDS:
        if field_name not in masks_obj:
            raise DeepProgramDatasetError(f"missing required mask field: {field_name}")
    consumer_modes = masks_obj["consumer_modes"]
    if not isinstance(consumer_modes, list) or not consumer_modes:
        raise DeepProgramDatasetError("masks.consumer_modes must be a non-empty list")
    for mode in consumer_modes:
        if mode not in ALLOWED_CONSUMER_MODES:
            raise DeepProgramDatasetError(_allowed_error("consumer_mode", str(mode), ALLOWED_CONSUMER_MODES))
    for field_name in REQUIRED_MASK_FIELDS[1:]:
        if not isinstance(masks_obj[field_name], bool):
            raise DeepProgramDatasetError(f"masks.{field_name} must be a boolean")
    if not any(masks_obj[field_name] for field_name in REQUIRED_MASK_FIELDS[1:]):
        raise DeepProgramDatasetError("at least one model input mask must be enabled")
    _validate_mask_consistency(masks_obj)


def _validate_mask_consistency(masks: dict[str, Any]) -> None:
    modes = set(masks["consumer_modes"])
    if "sequence" in modes and not masks["use_program_events"]:
        raise DeepProgramDatasetError("sequence consumers require program events")
    if "sequence" in modes and not masks["use_variable_state_sequence"]:
        raise DeepProgramDatasetError("sequence consumers require variable state sequence")
    if "graph" in modes and not masks["use_dependency_graph"]:
        raise DeepProgramDatasetError("graph consumers require dependency graph")
    if "hybrid" in modes and not all(
        masks[field_name] for field_name in REQUIRED_MASK_FIELDS[1:]
    ):
        raise DeepProgramDatasetError("hybrid consumers require event, state, and graph inputs")


def _validate_feature_names(feature_names: Any) -> None:
    feature_obj = _require_object(feature_names, "feature_names")
    for field_name in REQUIRED_FEATURE_NAME_FIELDS:
        if field_name not in feature_obj:
            raise DeepProgramDatasetError(f"missing required feature_names field: {field_name}")
        _validate_string_list(feature_obj[field_name], f"feature_names.{field_name}")


def _feature_names_or_default(feature_names: dict[str, list[str]] | None) -> dict[str, list[str]]:
    if feature_names is None:
        return {key: list(value) for key, value in DEFAULT_FEATURE_NAMES.items()}
    _validate_feature_names(feature_names)
    return {key: list(value) for key, value in feature_names.items()}


def _require_non_empty_list(value: Any, name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise DeepProgramDatasetError(f"{name} must be a non-empty list")
    if not all(isinstance(item, dict) for item in value):
        raise DeepProgramDatasetError(f"{name} must contain only objects")
    return value


def _validate_string_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not value:
        raise DeepProgramDatasetError(f"{name} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise DeepProgramDatasetError(f"{name} must contain only non-empty strings")


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DeepProgramDatasetError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise DeepProgramDatasetError(f"{name} must be a non-empty string")
    return value


def _reject_forbidden_public_fields(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_PUBLIC_FIELD_KEYS:
                raise DeepProgramDatasetError(
                    f"public-safe deep program sample must not contain raw field: {path}.{key_text}"
                )
            _reject_forbidden_public_fields(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_public_fields(child, f"{path}[{index}]")


def _allowed_error(name: str, value: str, allowed: set[str]) -> str:
    return f"invalid {name}: {value!r}; allowed: {', '.join(sorted(allowed))}"
