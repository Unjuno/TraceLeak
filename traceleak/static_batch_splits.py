"""Train/eval split helpers for static DeepProgramSample batches."""

from __future__ import annotations

from typing import Any

STATIC_BATCH_SPLIT_FORMAT = "traceleak.static_batch_split.v1"


class StaticBatchSplitError(ValueError):
    """Raised when a static batch cannot be split."""


def split_static_batch_by_module(
    *,
    batch: dict[str, Any],
    eval_modules: set[str],
) -> dict[str, Any]:
    """Split a static batch by module label."""

    _validate_batch(batch)
    if not isinstance(eval_modules, set) or not eval_modules:
        raise StaticBatchSplitError("eval_modules must be a non-empty set")
    train_sample_ids: list[str] = []
    eval_sample_ids: list[str] = []
    sample_modules: dict[str, str] = {}
    for sample in batch["samples"]:
        sample_id = str(sample["sample_id"])
        module_name = _module_from_sample(sample)
        sample_modules[sample_id] = module_name
        if module_name in eval_modules:
            eval_sample_ids.append(sample_id)
        else:
            train_sample_ids.append(sample_id)
    if not train_sample_ids:
        raise StaticBatchSplitError("train split must not be empty")
    if not eval_sample_ids:
        raise StaticBatchSplitError("eval split must not be empty")
    return {
        "format": STATIC_BATCH_SPLIT_FORMAT,
        "batch_id": batch["batch_id"],
        "train_sample_ids": train_sample_ids,
        "eval_sample_ids": eval_sample_ids,
        "metadata": {
            "split_strategy": "module_holdout",
            "eval_modules": sorted(eval_modules),
            "sample_modules": sample_modules,
            "train_count": len(train_sample_ids),
            "eval_count": len(eval_sample_ids),
        },
    }


def _module_from_sample(sample: dict[str, Any]) -> str:
    label = sample["labels"]["training_target"]["class"]
    if not isinstance(label, str) or not label.startswith("module:"):
        raise StaticBatchSplitError("sample training_target class must use module:<name>")
    return label.split(":", 1)[1]


def _validate_batch(batch: dict[str, Any]) -> None:
    if not isinstance(batch, dict):
        raise StaticBatchSplitError("batch must be an object")
    for field_name in ("batch_id", "samples"):
        if field_name not in batch:
            raise StaticBatchSplitError(f"missing required batch field: {field_name}")
    if not isinstance(batch["samples"], list) or not batch["samples"]:
        raise StaticBatchSplitError("batch samples must be a non-empty list")
