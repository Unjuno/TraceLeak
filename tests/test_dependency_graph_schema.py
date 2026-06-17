import pytest

from traceleak.dependency_graph_schema import (
    DependencyGraph,
    DependencyGraphEdge,
    DependencyGraphNode,
    DependencyGraphSchemaError,
    dependency_graph_from_dict,
    dependency_graph_from_program_events_and_variable_states,
    graph_edge_from_dict,
    graph_node_from_dict,
    sort_graph_edges,
    sort_graph_nodes,
    validate_dependency_graph,
    validate_graph_edge,
    validate_graph_node,
)
from traceleak.variable_state_sequence import variable_state_records_from_program_events


def sample_node() -> dict:
    return {
        "node_id": "variable:synthetic_keygen:branch_taken",
        "node_type": "variable",
        "label": "branch_taken",
        "source_event_id": "evt_000001",
        "time_step": 1,
        "metadata": {
            "scope": "synthetic_keygen",
            "taint_class": "secret_derived",
            "public_safe": True,
        },
    }


def sample_edge() -> dict:
    return {
        "edge_id": (
            "edge:writes:evt_000001:branch_evt_000001_branch:"
            "variable_synthetic_keygen_branch_taken"
        ),
        "edge_type": "writes",
        "source_node_id": "branch:evt_000001:branch",
        "target_node_id": "variable:synthetic_keygen:branch_taken",
        "source_event_id": "evt_000001",
        "time_step": 1,
        "metadata": {
            "derivation_method": "variable_state_record",
            "confidence": "explicit_record",
        },
    }


def sample_program_event() -> dict:
    return {
        "event_id": "evt_000001",
        "time_step": 1,
        "event_type": "branch",
        "operation": "branch",
        "function": "synthetic_keygen",
        "source_location": {
            "file": "examples/synthetic/target.c",
            "line": 21,
        },
        "variable_reads": ["candidate_bucket", "branch_guard"],
        "variable_writes": ["branch_taken"],
        "value_class": "redacted",
        "dependency_tags": ["control_flow", "secret_derived_path"],
        "control_context": {
            "phase": "synthetic_leak",
            "value_bucket": "taken",
        },
        "metadata": {
            "target": "synthetic-leak",
            "view": "redacted",
            "public_safe": True,
        },
    }


def sample_graph() -> dict:
    return {
        "graph_id": "graph_000001",
        "format": "traceleak.dependency_graph.v1",
        "nodes": [
            {
                "node_id": "branch:evt_000001:branch",
                "node_type": "branch",
                "label": "branch",
                "source_event_id": "evt_000001",
                "time_step": 1,
                "metadata": {"derivation_method": "program_event_operation"},
            },
            sample_node(),
        ],
        "edges": [sample_edge()],
        "metadata": {
            "graph_kind": "coarse_dependency_graph",
            "public_safe": True,
        },
    }


def test_validate_graph_node_accepts_full_node() -> None:
    node = sample_node()
    validate_graph_node(node)
    parsed = graph_node_from_dict(node)
    assert isinstance(parsed, DependencyGraphNode)
    assert parsed.to_dict() == node


def test_validate_graph_node_rejects_missing_field() -> None:
    node = sample_node()
    del node["node_type"]
    with pytest.raises(DependencyGraphSchemaError, match="missing required graph node field"):
        validate_graph_node(node)


def test_validate_graph_node_rejects_raw_payload_metadata() -> None:
    node = sample_node()
    node["metadata"]["raw_capture"] = "not-public-safe"
    with pytest.raises(DependencyGraphSchemaError, match="raw field"):
        validate_graph_node(node)


def test_validate_graph_edge_accepts_full_edge() -> None:
    edge = sample_edge()
    validate_graph_edge(edge)
    parsed = graph_edge_from_dict(edge)
    assert isinstance(parsed, DependencyGraphEdge)
    assert parsed.to_dict() == edge


def test_validate_graph_edge_rejects_self_loop() -> None:
    edge = sample_edge()
    edge["target_node_id"] = edge["source_node_id"]
    with pytest.raises(DependencyGraphSchemaError, match="self-loop"):
        validate_graph_edge(edge)


def test_dependency_graph_accepts_full_graph() -> None:
    graph = sample_graph()
    validate_dependency_graph(graph)
    parsed = dependency_graph_from_dict(graph)
    assert isinstance(parsed, DependencyGraph)
    assert parsed.to_dict() == graph


def test_dependency_graph_rejects_duplicate_node_id() -> None:
    graph = sample_graph()
    graph["nodes"].append(dict(graph["nodes"][0]))
    with pytest.raises(DependencyGraphSchemaError, match="duplicate node_id"):
        validate_dependency_graph(graph)


def test_dependency_graph_rejects_missing_edge_node_reference() -> None:
    graph = sample_graph()
    graph["edges"][0]["target_node_id"] = "variable:missing"
    with pytest.raises(DependencyGraphSchemaError, match="missing target node"):
        validate_dependency_graph(graph)


def test_sort_graph_nodes_and_edges_are_deterministic() -> None:
    later_node = sample_node()
    later_node["node_id"] = "variable:synthetic_keygen:candidate_bucket"
    later_node["label"] = "candidate_bucket"
    later_node["time_step"] = 2
    sorted_nodes = sort_graph_nodes([later_node, sample_graph()["nodes"][0], sample_node()])
    assert [node["node_id"] for node in sorted_nodes] == [
        "branch:evt_000001:branch",
        "variable:synthetic_keygen:branch_taken",
        "variable:synthetic_keygen:candidate_bucket",
    ]

    later_edge = sample_edge()
    later_edge["edge_id"] = "edge:reads:evt_000002:variable:operation"
    later_edge["edge_type"] = "reads"
    later_edge["time_step"] = 2
    sorted_edges = sort_graph_edges([later_edge, sample_edge()])
    assert [edge["edge_type"] for edge in sorted_edges] == ["writes", "reads"]


def test_dependency_graph_from_program_events_and_variable_states_builds_coarse_graph() -> None:
    event = sample_program_event()
    state_records = variable_state_records_from_program_events([event], sequence_id="seq_from_event")
    graph = dependency_graph_from_program_events_and_variable_states(
        [event],
        state_records,
        graph_id="graph_from_state",
    )

    validate_dependency_graph(graph)
    node_ids = {node["node_id"] for node in graph["nodes"]}
    assert "event:evt_000001" in node_ids
    assert "branch:evt_000001:branch" in node_ids
    assert "variable:synthetic_keygen:branch_taken" in node_ids
    assert "variable:synthetic_keygen:candidate_bucket" in node_ids
    assert "variable:synthetic_keygen:branch_guard" in node_ids

    edge_types = [edge["edge_type"] for edge in graph["edges"]]
    assert "controls" in edge_types
    assert edge_types.count("reads") == 2
    assert edge_types.count("writes") == 1
    assert edge_types.count("depends_on") == 2
    assert graph["metadata"]["graph_kind"] == "coarse_dependency_graph"
    assert graph["metadata"]["claim_scope"] == "representation_only_not_leakage_proof"


def test_dependency_graph_builder_rejects_state_for_missing_event() -> None:
    event = sample_program_event()
    state_records = variable_state_records_from_program_events([event], sequence_id="seq_from_event")
    state_records[0]["source_event_id"] = "evt_missing"
    with pytest.raises(DependencyGraphSchemaError, match="missing ProgramEvent"):
        dependency_graph_from_program_events_and_variable_states([event], state_records)
