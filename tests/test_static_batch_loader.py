from traceleak.static_batch_artifacts import write_static_batch_artifacts, write_static_batch_split_artifact
from traceleak.static_batch_loader import load_static_batch_index, load_static_split_samples
from traceleak.static_batch_splits import split_static_batch_by_module
from traceleak.static_sample_batches import build_static_module_sample_batch


def test_static_batch_loader_reads_train_and_eval_samples(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    (tmp_path / "crypto" / "evp").mkdir(parents=True)
    for path in [
        tmp_path / "crypto" / "bn" / "bn_demo.c",
        tmp_path / "crypto" / "evp" / "evp_demo.c",
    ]:
        path.write_text(
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
    split = split_static_batch_by_module(batch=batch, eval_modules={"crypto/evp"})
    output_dir = tmp_path / "artifacts"
    write_static_batch_artifacts(batch=batch, output_dir=output_dir)
    write_static_batch_split_artifact(split=split, output_dir=output_dir)

    index = load_static_batch_index(output_dir)
    train_samples = load_static_split_samples(artifact_dir=output_dir, split_name="train", consumer_mode="hybrid")
    eval_samples = load_static_split_samples(artifact_dir=output_dir, split_name="eval", consumer_mode="hybrid")

    assert index["sample_count"] == 2
    assert len(train_samples) == 1
    assert len(eval_samples) == 1
    assert train_samples[0]["masks"]["use_dependency_graph"] is True
    assert eval_samples[0]["masks"]["use_program_events"] is True
