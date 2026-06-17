"""Tensor contract schema v1 for model consumers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TENSOR_CONTRACT_FORMAT = "traceleak.tensor_contract.v1"

ALLOWED_TENSOR_CONSUMER_MODES: set[str] = {
    "graph",
    "hybrid",
    "sequence",
}

SEQUENCE_TENSOR_FIELDS: tuple[str, ...] = (
    "event_token_ids",
    "event_type_ids",
    "time_step_ids",
    "variable_state_ids",
    "attention_mask",
)

GRAPH_TENSOR_FIELDS: tuple[str, ...] = (
    "node_feature_ids",
    "edge_index",
    "edge_type_ids",
    "node_time_step_ids",
    "graph_mask",
)


class TensorContractError(ValueError):
    """Raised when a tensor contract is invalid."""


@dataclass(frozen=True)
class TensorContract:
    """Schema-level tensor field contract for model consumers."""

    sample_id: str
    consumer_mode: str
    tensor_fields: dict[str, list[str]]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""

        return {
            "sample_id": self.sample_id,
            "format": TENSOR_CONTRACT_FORMAT,
            "consumer_mode": self.consumer_mode,
            "tensor_fields": {key: list(value) for key, value in self.tensor_fields.items()},
            "metadata": dict(self.metadata),
        }


def tensor_fields_for_consumer_mode(consumer_mode: str) -> dict[str, list[str]]:
    """Return tensor field groups for a consumer mode."""

    if consumer_mode not in ALLOWED_TENSOR_CONSUMER_MODES:
        raise TensorContractError(f"invalid consumer_mode: {consumer_mode!r}")
    fields: dict[str, list[str]] = {}
    if consumer_mode in {"sequence", "hybrid"}:
        fields["sequence"] = list(SEQUENCE_TENSOR_FIELDS)
    if consumer_mode in {"graph", "hybrid"}:
        fields["graph"] = list(GRAPH_TENSOR_FIELDS)
    return fields
