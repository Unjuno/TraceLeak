"""Tensor contract schema v1 for model consumers."""

from __future__ import annotations

TENSOR_CONTRACT_FORMAT = "traceleak.tensor_contract.v1"

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
