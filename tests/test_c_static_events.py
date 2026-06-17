from traceleak.c_static_events import c_paths_to_program_events
from traceleak.deep_program_dataset import DEEP_PROGRAM_DATASET_FORMAT
from traceleak.static_program_sample import build_static_program_deep_sample


def test_c_paths_to_program_events_extracts_line_events(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    target = tmp_path / "crypto" / "bn" / "bn_demo.c"
    target.write_text(
        "int helper(int value) { return value; }\n"
        "int demo(int a, int b) {\n"
        "    int c = helper(a + b);\n"
        "    if (c) { return c; }\n"
        "    return b;\n"
        "}\n",
        encoding="utf-8",
    )

    events = c_paths_to_program_events(root=tmp_path, relative_paths=["crypto/bn/bn_demo.c"])
    assignment_events = [event for event in events if event["operation"] == "assign"]
    branch_events = [event for event in events if event["operation"] == "branch"]

    assert events
    assert all(event["source_location"]["file"] == "crypto/bn/bn_demo.c" for event in events)
    assert assignment_events
    assert any(event["variable_writes"] for event in events)
    assert any("helper" in event["control_context"]["call_targets"] for event in events)
    assert any(event["metadata"]["call_target_count"] > 0 for event in events)
    assert any(event["control_context"]["assignment_lhs"] == "c" for event in assignment_events)
    assert any("a" in event["control_context"]["assignment_rhs_identifiers"] for event in assignment_events)
    assert any("c" in event["control_context"]["branch_condition_identifiers"] for event in branch_events)


def test_build_static_program_deep_sample_from_c_file(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    target = tmp_path / "crypto" / "bn" / "bn_demo.c"
    target.write_text(
        "int helper(int value) { return value; }\n"
        "int demo(int a, int b) {\n"
        "    int c = helper(a + b);\n"
        "    if (c) { return c; }\n"
        "    return b;\n"
        "}\n",
        encoding="utf-8",
    )

    sample = build_static_program_deep_sample(
        root=tmp_path,
        relative_paths=["crypto/bn/bn_demo.c"],
        sample_id="static_sample_000001",
    )
    graph = sample["dependency_graph"]

    assert sample["format"] == DEEP_PROGRAM_DATASET_FORMAT
    assert sample["program_events"]
    assert sample["variable_state_sequence"]
    assert graph["nodes"]
    assert graph["metadata"]["static_call_graph_augmented"] is True
    assert any(node["label"] == "call_target:helper" for node in graph["nodes"])
    assert any(edge["edge_type"] == "observes" for edge in graph["edges"])
