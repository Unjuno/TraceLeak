from traceleak.c_static_events import c_paths_to_program_events
from traceleak.deep_program_dataset import DEEP_PROGRAM_DATASET_FORMAT
from traceleak.static_program_sample import build_static_program_deep_sample


def test_c_paths_to_program_events_extracts_line_events(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    target = tmp_path / "crypto" / "bn" / "bn_demo.c"
    target.write_text(
        "int demo(int a, int b) {\n"
        "    int c = a + b;\n"
        "    if (c) { return c; }\n"
        "    return b;\n"
        "}\n",
        encoding="utf-8",
    )

    events = c_paths_to_program_events(root=tmp_path, relative_paths=["crypto/bn/bn_demo.c"])

    assert events
    assert all(event["source_location"]["file"] == "crypto/bn/bn_demo.c" for event in events)
    assert any(event["operation"] == "assign" for event in events)
    assert any(event["variable_writes"] for event in events)


def test_build_static_program_deep_sample_from_c_file(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    target = tmp_path / "crypto" / "bn" / "bn_demo.c"
    target.write_text(
        "int demo(int a, int b) {\n"
        "    int c = a + b;\n"
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

    assert sample["format"] == DEEP_PROGRAM_DATASET_FORMAT
    assert sample["program_events"]
    assert sample["variable_state_sequence"]
    assert sample["dependency_graph"]["nodes"]
