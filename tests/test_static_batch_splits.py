from traceleak.static_batch_splits import STATIC_BATCH_SPLIT_FORMAT, split_static_batch_by_module
from traceleak.static_sample_batches import build_static_module_sample_batch


def test_split_static_batch_by_module_holds_out_eval_module(tmp_path) -> None:
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

    assert split["format"] == STATIC_BATCH_SPLIT_FORMAT
    assert split["metadata"]["split_strategy"] == "module_holdout"
    assert len(split["train_sample_ids"]) == 1
    assert len(split["eval_sample_ids"]) == 1
    assert split["metadata"]["eval_modules"] == ["crypto/evp"]
