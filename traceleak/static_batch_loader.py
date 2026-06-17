"""Load static DeepProgramSample batch artifacts for model consumers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from traceleak.deep_program_dataset import deep_program_sample_from_dict

STATIC_BATCH_LOADER_FORMAT = "traceleak.static_batch_loader.v1"


class StaticBatchLoaderError(ValueError):
    """Raised when static batch artifacts cannot be loaded."""


def load_static_batch_index(artifact_dir: Path) -> dict[str, Any]:
    """Load index.json from a static batch artifact directory."""

    path = Path(artifact_dir) / "index.json"
    if not path.exists() or not path.is_file():
        raise StaticBatchLoaderError(f"index.json not found: {path}")
    index = json.loads(path.read_text(encoding="utf-8"))
    _validate_index(index)
    return index


def load_static_batch_split(artifact_dir: Path) -> dict[str, Any]:
    """Load split.json from a static batch artifact directory."""

    path = Path(artifact_dir) / "split.json"
    if not path.exists() or not path.is_file():
        raise StaticBatchLoaderError(f"split.json not found: {path}")
    split = json.loads(path.read_text(encoding="utf-8"))
    _validate_split(split)
    return split


def load_static_sample(artifact_dir: Path, sample_entry: dict[str, Any]) -> dict[str, Any]:
    """Load and validate one DeepProgramSample referenced by an index entry."""

    _validate_sample_entry(sample_entry)
    path = Path(artifact_dir) / str(sample_entry["filename"])
    if not path.exists() or not path.is_file():
        raise StaticBatchLoaderError(f"sample file not found: {path}")
    sample = json.loads(path.read_text(encoding="utf-8"))
    parsed = deep_program_sample_from_dict(sample)
    return parsed.to_dict()


def iter_static_samples(
    *,
    artifact_dir: Path,
    sample_ids: Iterable[str] | None = None,
    consumer_mode: str | None = None,
) -> list[dict[str, Any]]:
    """Load selected static DeepProgramSample records from artifact_dir."""

    index = load_static_batch_index(artifact_dir)
    wanted_ids = set(sample_ids) if sample_ids is not None else None
    samples: list[dict[str, Any]] = []
    for entry in index["samples"]:
        if wanted_ids is not None and entry["sample_id"] not in wanted_ids:
            continue
        sample = load_static_sample(artifact_dir, entry)
        if consumer_mode is not None:
            _require_consumer_mode(sample, consumer_mode)
        samples.append(sample)
    return samples


def load_static_split_samples(
    *,
    artifact_dir: Path,
    split_name: str,
    consumer_mode: str | None = None,
) -> list[dict[str, Any]]:
    """Load train or eval samples according to split.json."""

    split = load_static_batch_split(artifact_dir)
    if split_name == "train":
        sample_ids = split["train_sample_ids"]
    elif split_name == "eval":
        sample_ids = split["eval_sample_ids"]
    else:
        raise StaticBatchLoaderError("split_name must be 'train' or 'eval'")
    return iter_static_samples(
        artifact_dir=artifact_dir,
        sample_ids=sample_ids,
        consumer_mode=consumer_mode,
    )


def _require_consumer_mode(sample: dict[str, Any], consumer_mode: str) -> None:
    modes = sample["masks"]["consumer_modes"]
    if consumer_mode not in modes:
        raise StaticBatchLoaderError(f"sample does not support consumer_mode: {consumer_mode}")


def _validate_index(index: dict[str, Any]) -> None:
    if not isinstance(index, dict):
        raise StaticBatchLoaderError("index must be an object")
    for field_name in ("format", "batch_id", "samples"):
        if field_name not in index:
            raise StaticBatchLoaderError(f"missing required index field: {field_name}")
    if not isinstance(index["samples"], list):
        raise StaticBatchLoaderError("index samples must be a list")


def _validate_split(split: dict[str, Any]) -> None:
    if not isinstance(split, dict):
        raise StaticBatchLoaderError("split must be an object")
    for field_name in ("format", "batch_id", "train_sample_ids", "eval_sample_ids"):
        if field_name not in split:
            raise StaticBatchLoaderError(f"missing required split field: {field_name}")
    if not isinstance(split["train_sample_ids"], list) or not isinstance(split["eval_sample_ids"], list):
        raise StaticBatchLoaderError("split sample ids must be lists")


def _validate_sample_entry(entry: dict[str, Any]) -> None:
    if not isinstance(entry, dict):
        raise StaticBatchLoaderError("sample entry must be an object")
    for field_name in ("sample_id", "filename"):
        if field_name not in entry:
            raise StaticBatchLoaderError(f"missing required sample entry field: {field_name}")
