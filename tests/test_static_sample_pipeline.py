from traceleak.deep_program_dataset import DEEP_PROGRAM_DATASET_FORMAT
from traceleak.static_sample_pipeline import build_static_sample_from_tree


def test_build_static_sample_from_tree(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    (tmp_path / "crypto" / "bn" / "bn_demo.c").write_text(
        "int demo(int a, int b) {\n"
        "    int c = a + b;\n"
        "    if (c) { return c; }\n"
        "    return b;\n"
        "}\n",
        encoding="utf-8",
    )

    sample = build_static_sample_from_tree(
        root=tmp_path,
        sample_id="static_tree_sample_000001",
        max_paths=8,
    )

    assert sample["format"] == DEEP_PROGRAM_DATASET_FORMAT
    assert sample["program_events"]
    assert sample["variable_state_sequence"]
    assert sample["dependency_graph"]["nodes"]
