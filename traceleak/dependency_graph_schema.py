"""Dependency Graph Schema v1 for Deep Program Representation.

This module represents program events, operations, variables, and coarse
read/write dependencies as a graph.  The graph builder is conservative: it only
uses explicit ProgramEvent and VariableStateRecord fields, and marks derived
edges with metadata so later analyses can replace coarse edges with stronger
reaching-definition or data-flow evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from traceleak.program_event_schema import FORBIDDEN_PUBLIC_FIELD_KEYS, sort_program_events
from traceleak.variable_state_sequence import sort_variable_state_sequence

DEPENDENCY_GRAPH_SCHEMA_FORMAT = "traceleak.dependency_graph.v1"

ALLOWED_GRAPH_NODE_TYPES: set[str] = {
    "branch",
    "event",
    "memory_access",
    "observable_output",
    "operation",
    "variable",
}

ALLOWED_GRAPH_EDGE_TYPES: set[str] = {
    "controls",
    "depends_on",
    "derives",
    "observes",
    "reads",
    "writes",
}

REQUIRED_GRAPH_NODE_FIELDS: tuple[str, ...] = (
    "node_id",
    "node_type",
    "label",
    "source_event_id",
    "time_step",
    "metadata",
)

REQUIRED_GRAPH_EDGE_FIELDS: tuple[str, ...] = (
    "edge_id",
    "edge_type",
    "source_node_id",
    "target_node_id",
    "source_event_id",
    "time_step",
    "metadata",
)


class DependencyGraphSchemaError(ValueError):
    """Raised when a dependency graph record is invalid."""


@dataclass(frozen=True)
class DependencyGraphNode:
    """Normalized graph node for events, operations, or variables."""

    node_id: str
    node_type: str
    label: str
    source_event_id: str
    time_step: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic dictionary representation."""

        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "source_event_id": self.source_event_id,
            "time_step": self.time_step,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DependencyGraphEdge:
    """Normalized graph edge between dependency graph nodes."""

    edge_id: str
    edge_type: str
    source_node_id: str
    target_node_id: str
    source_event_id: str
    time_step: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic dictionary representation."""

        return {
            "edge_id": self.edge_id,
            "edge_type": self.edge_type,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "source_event_id": self.source_event_id,
            "time_step": self.time_step,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DependencyGraph:
    """Dependency graph container consumed by later deep dataset builders."""

    graph_id: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic dictionary representation."""

        return {
            "graph_id": self.graph_id,
            "format": DEPENDENCY_GRAPH_SCHEMA_FORMAT,
            "nodes": [dict(node) for node in self.nodes],
            "edges": [dict(edge) for edge in self.edges],
            "metadata": dict(self.metadata),
        }


def graph_node_from_dict(data: dict[str, Any], *, public_safe: bool = True) -> DependencyGraphNode:
    """Validate and convert a dictionary into a DependencyGraphNode."""

    validate_graph_node(data, public_safe=public_safe)
    return DependencyGraphNode(
        node_id=data["node_id"],
        node_type=data["node_type"],
        label=data["label"],
        source_event_id=data["source_event_id"],
        time_step=data["time_step"],
        metadata=dict(data["metadata"]),
    )


def graph_edge_from_dict(data: dict[str, Any], *, public_safe: bool = True) -> DependencyGraphEdge:
    """Validate and convert a dictionary into a DependencyGraphEdge."""

    validate_graph_edge(data, public_safe=public_safe)
    return DependencyGraphEdge(
        edge_id=data["edge_id"],
        edge_type=data["edge_type"],
        source_node_id=data["source_node_id"],
        target_node_id=data["target_node_id"],
        source_event_id=data["source_event_id"],
        time_step=data["time_step"],
        metadata=dict(data["metadata"]),
    )


def dependency_graph_from_dict(data: dict[str, Any], *, public_safe: bool = True) -> DependencyGraph:
    """Validate and convert a dictionary into a DependencyGraph."""

    validate_dependency_graph(data, public_safe=public_safe)
    return DependencyGraph(
        graph_id=data["graph_id"],
        nodes=[dict(node) for node in data["nodes"]],
        edges=[dict(edge) for edge in data["edges"]],
        metadata=dict(data["metadata"]),
    )


def validate_graph_node(node: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate one dependency graph node."""

    if not isinstance(node, dict):
        raise DependencyGraphSchemaError("graph node must be an object")
    for field_name in REQUIRED_GRAPH_NODE_FIELDS:
        if field_name not in node:
            raise DependencyGraphSchemaError(f"missing required graph node field: {field_name}")

    _require_non_empty_string(node["node_id"], "node_id")
    node_type = _require_non_empty_string(node["node_type"], "node_type")
    if node_type not in ALLOWED_GRAPH_NODE_TYPES:
        raise DependencyGraphSchemaError(_allowed_error("node_type", node_type, ALLOWED_GRAPH_NODE_TYPES))
    _require_non_empty_string(node["label"], "label")
    _require_non_empty_string(node["source_event_id"], "source_event_id")
    _validate_time_step(node["time_step"])
    _validate_object(node["metadata"], "metadata")

    if public_safe:
        _reject_forbidden_public_fields(node, "node")


def validate_graph_edge(edge: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate one dependency graph edge."""

    if not isinstance(edge, dict):
        raise DependencyGraphSchemaError("graph edge must be an object")
    for field_name in REQUIRED_GRAPH_EDGE_FIELDS:
        if field_name not in edge:
            raise DependencyGraphSchemaError(f"missing required graph edge field: {field_name}")

    _require_non_empty_string(edge["edge_id"], "edge_id")
    edge_type = _require_non_empty_string(edge["edge_type"], "edge_type")
    if edge_type not in ALLOWED_GRAPH_EDGE_TYPES:
        raise DependencyGraphSchemaError(_allowed_error("edge_type", edge_type, ALLOWED_GRAPH_EDGE_TYPES))
    _require_non_empty_string(edge["source_node_id"], "source_node_id")
    _require_non_empty_string(edge["target_node_id"], "target_node_id")
    if edge["source_node_id"] == edge["target_node_id"]:
        raise DependencyGraphSchemaError("graph edge must not be a self-loop")
    _require_non_empty_string(edge["source_event_id"], "source_event_id")
    _validate_time_step(edge["time_step"])
    _validate_object(edge["metadata"], "metadata")

    if public_safe:
        _reject_forbidden_public_fields(edge, "edge")


def validate_dependency_graph(graph: dict[str, Any], *, public_safe: bool = True) -> None:
    """Validate a full Dependency Graph Schema v1 dictionary."""

    if not isinstance(graph, dict):
        raise DependencyGraphSchemaError("dependency graph must be an object")
    for field_name in ("graph_id", "format", "nodes", "edges", "metadata"):
        if field_name not in graph:
            raise DependencyGraphSchemaError(f"missing required dependency graph field: {field_name}")
    _require_non_empty_string(graph["graph_id"], "graph_id")
    if graph["format"] != DEPENDENCY_GRAPH_SCHEMA_FORMAT:
        raise DependencyGraphSchemaError(
            f"invalid dependency graph format: {graph['format']!r}; expected: {DEPENDENCY_GRAPH_SCHEMA_FORMAT}"
        )
    if not isinstance(graph["nodes"], list) or not graph["nodes"]:
        raise DependencyGraphSchemaError("dependency graph nodes must be a non-empty list")
    if not isinstance(graph["edges"], list):
        raise DependencyGraphSchemaError("dependency graph edges must be a list")
    _validate_object(graph["metadata"], "metadata")

    node_ids: set[str] = set()
    for index, node in enumerate(graph["nodes"]):
        try:
            validate_graph_node(node, public_safe=public_safe)
        except DependencyGraphSchemaError as exc:
            raise DependencyGraphSchemaError(f"nodes[{index}]: {exc}") from exc
        node_id = str(node["node_id"])
        if node_id in node_ids:
            raise DependencyGraphSchemaError(f"duplicate node_id: {node_id}")
        node_ids.add(node_id)

    edge_ids: set[str] = set()
    for index, edge in enumerate(graph["edges"]):
        try:
            validate_graph_edge(edge, public_safe=public_safe)
        except DependencyGraphSchemaError as exc:
            raise DependencyGraphSchemaError(f"edges[{index}]: {exc}") from exc
        edge_id = str(edge["edge_id"])
        if edge_id in edge_ids:
            raise DependencyGraphSchemaError(f"duplicate edge_id: {edge_id}")
        if edge["source_node_id"] not in node_ids:
            raise DependencyGraphSchemaError(f"edge references missing source node: {edge['source_node_id']}")
        if edge["target_node_id"] not in node_ids:
            raise DependencyGraphSchemaError(f"edge references missing target node: {edge['target_node_id']}")
        edge_ids.add(edge_id)

    if public_safe:
        _reject_forbidden_public_fields(graph, "graph")


def sort_graph_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return graph nodes in deterministic order."""

    for node in nodes:
        validate_graph_node(node)
    return sorted(
        nodes,
        key=lambda node: (
            int(node["time_step"]),
            _node_type_sort_rank(str(node["node_type"])),
            str(node["node_id"]),
        ),
    )


def sort_graph_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return graph edges in deterministic order."""

    for edge in edges:
        validate_graph_edge(edge)
    return sorted(
        edges,
        key=lambda edge: (
            int(edge["time_step"]),
            _edge_type_sort_rank(str(edge["edge_type"])),
            str(edge["edge_id"]),
        ),
    )


def dependency_graph_from_program_events_and_variable_states(
    events: list[dict[str, Any]],
    variable_state_records: list[dict[str, Any]],
    *,
    graph_id: str = "coarse_dependency_graph",
) -> dict[str, Any]:
    """Build a coarse graph from ProgramEvent and VariableStateRecord records.

    The graph is not a proof of full data-flow.  It links explicit reads, writes,
    same-event local dependencies, and operation/control context only.
    """

    _require_non_empty_string(graph_id, "graph_id")
    ordered_events = sort_program_events(events)
    ordered_states = sort_variable_state_sequence(variable_state_records)
    event_by_id = {str(event["event_id"]): event for event in ordered_events}

    nodes_by_id: dict[str, dict[str, Any]] = {}
    edges_by_id: dict[str, dict[str, Any]] = {}
    operation_node_by_event_id: dict[str, str] = {}

    for event in ordered_events:
        event_node = _event_node_from_program_event(event)
        _add_node(nodes_by_id, event_node)
        operation_node = _operation_node_from_program_event(event)
        _add_node(nodes_by_id, operation_node)
        operation_node_by_event_id[event["event_id"]] = operation_node["node_id"]
        _add_edge(
            edges_by_id,
            _edge(
                edge_type="controls",
                source_node_id=event_node["node_id"],
                target_node_id=operation_node["node_id"],
                source_event_id=event["event_id"],
                time_step=event["time_step"],
                metadata={
                    "derivation_method": "program_event_operation_link",
                    "confidence": "coarse",
                },
            ),
        )

    for record in ordered_states:
        event = event_by_id.get(str(record["source_event_id"]))
        if event is None:
            raise DependencyGraphSchemaError(
                f"variable state references missing ProgramEvent: {record['source_event_id']}"
            )
        variable_node = _variable_node_from_state_record(record)
        _add_node(nodes_by_id, variable_node)
        operation_node_id = operation_node_by_event_id[str(record["source_event_id"])]
        edge_type = _state_class_to_edge_type(str(record["state_class"]))
        source_node_id, target_node_id = _state_edge_direction(
            edge_type=edge_type,
            operation_node_id=operation_node_id,
            variable_node_id=variable_node["node_id"],
        )
        _add_edge(
            edges_by_id,
            _edge(
                edge_type=edge_type,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                source_event_id=record["source_event_id"],
                time_step=record["time_step"],
                metadata={
                    "derivation_method": "variable_state_record",
                    "state_class": record["state_class"],
                    "taint_class": record["taint_class"],
                    "confidence": "explicit_record",
                },
            ),
        )
        for dependency in record.get("depends_on", []):
            dependency_node = _variable_node_from_dependency(record, str(dependency))
            _add_node(nodes_by_id, dependency_node)
            _add_edge(
                edges_by_id,
                _edge(
                    edge_type="depends_on",
                    source_node_id=dependency_node["node_id"],
                    target_node_id=variable_node["node_id"],
                    source_event_id=record["source_event_id"],
                    time_step=record["time_step"],
                    metadata={
                        "derivation_method": "same_event_variable_state_depends_on",
                        "state_class": record["state_class"],
                        "confidence": "coarse_local_dependency",
                    },
                ),
            )

    graph = {
        "graph_id": graph_id,
        "format": DEPENDENCY_GRAPH_SCHEMA_FORMAT,
        "nodes": sort_graph_nodes(list(nodes_by_id.values())),
        "edges": sort_graph_edges(list(edges_by_id.values())),
        "metadata": {
            "graph_kind": "coarse_dependency_graph",
            "derivation_method": "program_events_and_variable_state_records",
            "program_event_count": len(ordered_events),
            "variable_state_record_count": len(ordered_states),
            "claim_scope": "representation_only_not_leakage_proof",
        },
    }
    validate_dependency_graph(graph)
    return graph


def _event_node_from_program_event(event: dict[str, Any]) -> dict[str, Any]:
    node = {
        "node_id": f"event:{_slug(event['event_id'])}",
        "node_type": "event",
        "label": str(event["event_id"]),
        "source_event_id": event["event_id"],
        "time_step": event["time_step"],
        "metadata": {
            "event_type": event["event_type"],
            "operation": event["operation"],
            "function": event["function"],
            "derivation_method": "program_event",
        },
    }
    validate_graph_node(node)
    return node


def _operation_node_from_program_event(event: dict[str, Any]) -> dict[str, Any]:
    node_type = _operation_node_type(event)
    node = {
        "node_id": f"{node_type}:{_slug(event['event_id'])}:{_slug(event['operation'])}",
        "node_type": node_type,
        "label": str(event["operation"]),
        "source_event_id": event["event_id"],
        "time_step": event["time_step"],
        "metadata": {
            "event_type": event["event_type"],
            "operation": event["operation"],
            "function": event["function"],
            "derivation_method": "program_event_operation",
        },
    }
    validate_graph_node(node)
    return node


def _variable_node_from_state_record(record: dict[str, Any]) -> dict[str, Any]:
    node_id = _variable_node_id(scope=record["scope"], variable_id=record["variable_id"])
    node = {
        "node_id": node_id,
        "node_type": "variable",
        "label": str(record["variable_id"]),
        "source_event_id": record["source_event_id"],
        "time_step": record["time_step"],
        "metadata": {
            "scope": record["scope"],
            "taint_class": record["taint_class"],
            "is_secret_derived": record["is_secret_derived"],
            "derivation_method": "variable_state_record",
        },
    }
    validate_graph_node(node)
    return node


def _variable_node_from_dependency(record: dict[str, Any], variable_id: str) -> dict[str, Any]:
    node = {
        "node_id": _variable_node_id(scope=record["scope"], variable_id=variable_id),
        "node_type": "variable",
        "label": variable_id,
        "source_event_id": record["source_event_id"],
        "time_step": record["time_step"],
        "metadata": {
            "scope": record["scope"],
            "derivation_method": "variable_state_depends_on",
        },
    }
    validate_graph_node(node)
    return node


def _edge(
    *,
    edge_type: str,
    source_node_id: str,
    target_node_id: str,
    source_event_id: str,
    time_step: int,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    edge = {
        "edge_id": _edge_id(edge_type, source_node_id, target_node_id, source_event_id),
        "edge_type": edge_type,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "source_event_id": source_event_id,
        "time_step": time_step,
        "metadata": metadata,
    }
    validate_graph_edge(edge)
    return edge


def _add_node(nodes_by_id: dict[str, dict[str, Any]], node: dict[str, Any]) -> None:
    existing = nodes_by_id.get(str(node["node_id"]))
    if existing is not None and (
        existing["node_type"] != node["node_type"] or existing["label"] != node["label"]
    ):
        raise DependencyGraphSchemaError(f"conflicting node_id: {node['node_id']}")
    if existing is None:
        nodes_by_id[str(node["node_id"])] = node


def _add_edge(edges_by_id: dict[str, dict[str, Any]], edge: dict[str, Any]) -> None:
    existing = edges_by_id.get(str(edge["edge_id"]))
    if existing is not None and existing != edge:
        raise DependencyGraphSchemaError(f"conflicting edge_id: {edge['edge_id']}")
    if existing is None:
        edges_by_id[str(edge["edge_id"])] = edge


def _operation_node_type(event: dict[str, Any]) -> str:
    event_type = str(event.get("event_type", ""))
    operation = str(event.get("operation", ""))
    if event_type == "branch" or operation == "branch":
        return "branch"
    if event_type == "memory" or operation in {"load", "store", "memory_access"}:
        return "memory_access"
    if event_type == "observable" or operation in {"observe", "timing_observation"}:
        return "observable_output"
    return "operation"


def _state_class_to_edge_type(state_class: str) -> str:
    if state_class == "read":
        return "reads"
    if state_class in {"write", "update"}:
        return "writes"
    if state_class == "observe":
        return "observes"
    if state_class == "control":
        return "controls"
    return "derives"


def _state_edge_direction(
    *, edge_type: str, operation_node_id: str, variable_node_id: str
) -> tuple[str, str]:
    if edge_type == "reads":
        return variable_node_id, operation_node_id
    return operation_node_id, variable_node_id


def _variable_node_id(*, scope: str, variable_id: str) -> str:
    return f"variable:{_slug(scope)}:{_slug(variable_id)}"


def _edge_id(edge_type: str, source_node_id: str, target_node_id: str, source_event_id: str) -> str:
    return f"edge:{edge_type}:{_slug(source_event_id)}:{_slug(source_node_id)}:{_slug(target_node_id)}"


def _validate_time_step(value: Any) -> None:
    if not isinstance(value, int) or value < 0:
        raise DependencyGraphSchemaError("time_step must be a non-negative integer")


def _validate_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DependencyGraphSchemaError(f"{name} must be an object")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise DependencyGraphSchemaError(f"{name} must be a non-empty string")
    return value


def _reject_forbidden_public_fields(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_PUBLIC_FIELD_KEYS:
                raise DependencyGraphSchemaError(
                    f"public-safe dependency graph must not contain raw field: {path}.{key_text}"
                )
            _reject_forbidden_public_fields(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_public_fields(child, f"{path}[{index}]")


def _node_type_sort_rank(node_type: str) -> int:
    order = {
        "event": 0,
        "operation": 1,
        "branch": 2,
        "memory_access": 3,
        "observable_output": 4,
        "variable": 5,
    }
    return order.get(node_type, len(order))


def _edge_type_sort_rank(edge_type: str) -> int:
    order = {
        "controls": 0,
        "reads": 1,
        "writes": 2,
        "depends_on": 3,
        "derives": 4,
        "observes": 5,
    }
    return order.get(edge_type, len(order))


def _slug(value: Any) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip())
    return slug.strip("_") or "unknown"


def _allowed_error(name: str, value: str, allowed: set[str]) -> str:
    return f"invalid {name}: {value!r}; allowed: {', '.join(sorted(allowed))}"
