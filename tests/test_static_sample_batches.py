from traceleak.static_sample_batches import STATIC_SAMPLE_BATCH_FORMAT, build_static_module_sample_batch


def test_build_static_module_sample_batch_groups_by_module(tmp_path) -> None:
    (tmp_path / "crypto" / "bn").mkdir(parents=True)
    (tmp_path / "crypto" / "evp").mkdir(parents=True)
    (tmp_path / "ssl" / "statem").mkdir(parents=True)
    for path in [
        tmp_path / "crypto" / "bn" / "bn_demo.c",
        tmp_path / "crypto" / "evp" / "evp_demo.c",
        tmp_path / "ssl" / "statem" / "statem_demo.c",
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
    summaries = batch["metadata"]["sample_summaries"]

    assert batch["format"] == STATIC_SAMPLE_BATCH_FORMAT
    assert batch["sample_count"] == 3
    assert len(batch["samples"]) == 3
    assert len(summaries) == 3
    assert all(sample["program_events"] for sample in batch["samples"])
    assert all(summary["event_count"] > 0 for summary in summaries)
    assert batch["metadata"]["total_event_count"] == sum(summary["event_count"] for summary in summaries)
    assert {sample["labels"]["training_target"]["class"] for sample in batch["samples"]} == {
        "module:crypto/bn",
        "module:crypto/evp",
        "module:ssl/statem",
    }
