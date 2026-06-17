import json

from traceleak.static_batch_artifacts import STATIC_BATCH_INDEX_FORMAT, write_static_batch_artifacts
from traceleak.static_sample_batches import build_static_module_sample_batch


def test_write_static_batch_artifacts_writes_index_and_samples(tmp_path) -> None:
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
    output_dir = tmp_path / "artifacts"

    index = write_static_batch_artifacts(batch=batch, output_dir=output_dir)
    written_index = json.loads((output_dir / "index.json").read_text(encoding="utf-8"))

    assert index == written_index
    assert index["format"] == STATIC_BATCH_INDEX_FORMAT
    assert index["sample_count"] == 1
    assert (output_dir / index["samples"][0]["filename"]).exists()
    assert index["metadata"]["total_event_count"] > 0
