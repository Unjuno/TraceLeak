from traceleak.deep_sample_consumers import sample_for_consumer_mode
from traceleak.static_sample_batches import build_static_module_sample_batch


def test_sample_for_consumer_mode_selects_expected_views(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    (tmp_path / "crypto" / "bn" / "bn_demo.c").write_text(
        "int helper(int value) { return value; }\n"
        "int demo(int a, int b) {\n"
        "    int c = helper(a + b);\n"
        "    if (c) { return c; }\n"
        "    return b;\n"
        "}\n",
        encoding="utf-8",
    )
    batch = build_static_module_sample_batch(
        root=tmp_path,
        batch_id="static_batch_000001",
        max_paths_per_module=2,
    )
    sample = batch["samples"][0]

    sequence_view = sample_for_consumer_mode(sample, "sequence")
    graph_view = sample_for_consumer_mode(sample, "graph")
    hybrid_view = sample_for_consumer_mode(sample, "hybrid")

    assert sorted(sequence_view["inputs"]) == ["program_events", "variable_state_sequence"]
    assert sorted(graph_view["inputs"]) == ["dependency_graph"]
    assert sorted(hybrid_view["inputs"]) == ["dependency_graph", "program_events", "variable_state_sequence"]
