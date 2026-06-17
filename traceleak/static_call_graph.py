"""Augment dependency graphs with static call-target observations."""

from __future__ import annotations

import re
from typing import Any

from traceleak.dependency_graph_schema import validate_dependency_graph

STATIC_CALL_GRAPH_AUGMENT_FORMAT = "traceleak.static_call_graph_augment.v1"


def augment_graph_with_static_calls(
    *,
    dependency_graph: dict[str, Any],
    program_events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a dependency graph with extra call-target observation edges."""

    validate_dependency_graph(dependency_graph)
    nodes_by_id = {str(node["node_id"]): dict(node) for node in dependency_graph["nodes"]}
    edges_by_id = {str(edge["edge_id"]): dict(edge) for edge in dependency_graph["edges"]}

    for event in program_events:
        call_targets = _call_targets_from_event(event)
        if not call_targets:
            continue
        event_id = str(event["event_id"])
        operation_node_id = _operation_node_id(event)
        if operation_node_id not in nodes_by_id:
            continue
        for target in call_targets:
            target_node = _call_target_node(event, target)
            nodes_by_id.setdefault(target_node["node_id"], target_node)
            edge = _call_observation_edge(
                event=event,
                operation_node_id=operation_node_id,
                target_node_id=target_node["node_id"],
            )
            edges_by_id.setdefault(edge["edge_id"], edge)

    graph = {
        "graph_id": dependency_graph["graph_id"],
        "format": dependency_graph["format"],
        "nodes": sorted(nodes_by_id.values(), key=lambda node: (int(node["time_step"]), str(node["node_id"]))),
        "edges": sorted(edges_by_id.values(), key=lambda edge: (int(edge["time_step"]), str(edge["edge_id"]))),
        "metadata": {
            **dict(dependency_graph["metadata"]),
            "static_call_graph_augment_format": STATIC_CALL_GRAPH_AUGMENT_FORMAT,
            "static_call_graph_augmented": True,
        },
    }
    validate_dependency_graph(graph)
    return graph


def _call_targets_from_event(event: dict[str, Any]) -> list[str]:
    context = event.get("control_context", {})
    if not isinstance(context, dict):
        return []
    targets = context.get("call_targets", [])
    if not isinstance(targets, list):
        return []
    return [str(target) for target in targets if isinstance(target, str) and target]


def _call_target_node(event: dict[str, Any], target: str) -> dict[str, Any]:
    return {
        "node_id": f"variable:call_target:{_slug(target)}",
        "node_type": "variable",
        "label": f"call_target:{target}",
        "source_event_id": event["event_id"],
        "time_step": event["time_step"],
        "metadata": {
            "scope": "static_call_target",
            "derivation_method": "static_call_target_observation",
        },
    }


def _call_observation_edge(
    *,
    event: dict[str, Any],
    operation_node_id: str,
    target_node_id: str,
) -> dict[str, Any]:
    edge_id = f"edge:observes:{_slug(event['event_id'])}:{_slug(operation_node_id)}:{_slug(target_node_id)}"
    return {
        "edge_id": edge_id,
        "edge_type": "observes",
        "source_node_id": operation_node_id,
        "target_node_id": target_node_id,
        "source_event_id": event["event_id"],
        "time_step": event["time_step"],
        "metadata": {
            "derivation_method": "static_call_target_observation",
            "confidence": "static_line_summary",
        },
    }


def _operation_node_id(event: dict[str, Any]) -> str:
    return f"{_operation_node_type(event)}:{_slug(event['event_id'])}:{_slug(event['operation'])}"


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


def _slug(value: Any) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip())
    return slug.strip("_") or "unknown"
