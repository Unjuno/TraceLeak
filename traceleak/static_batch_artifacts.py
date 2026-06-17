"""Artifact helpers for static DeepProgramSample batches."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATIC_BATCH_INDEX_FORMAT = "traceleak.static_batch_index.v1"


class StaticBatchArtifactError(ValueError):
    """Raised when static batch artifacts cannot be written."""


def write_static_batch_artifacts(
    *,
    batch: dict[str, Any],
    output_dir: Path,
    write_samples: bool = True,
) -> dict[str, Any]:
    """Write a static batch index and optional per-sample JSON files."""

    _validate_batch_shape(batch)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    sample_entries: list[dict[str, Any]] = []
    for sample in batch["samples"]:
        sample_id = str(sample["sample_id"])
        filename = f"{_safe_filename(sample_id)}.json"
        if write_samples:
            (output_path / filename).write_text(
                json.dumps(sample, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        sample_entries.append(_sample_index_entry(sample, filename))
    index = {
        "format": STATIC_BATCH_INDEX_FORMAT,
        "batch_id": batch["batch_id"],
        "sample_count": len(sample_entries),
        "samples": sample_entries,
        "metadata": {
            "source_batch_format": batch["format"],
            "write_samples": write_samples,
            "total_event_count": sum(entry["event_count"] for entry in sample_entries),
            "total_graph_edge_count": sum(entry["graph_edge_count"] for entry in sample_entries),
        },
    }
    (output_path / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return index


def static_batch_index_from_batch(batch: dict[str, Any]) -> dict[str, Any]:
    """Build an in-memory lightweight index for a static batch."""

    _validate_batch_shape(batch)
    sample_entries = [_sample_index_entry(sample, f"{_safe_filename(sample['sample_id'])}.json") for sample in batch["samples"]]
    return {
        "format": STATIC_BATCH_INDEX_FORMAT,
        "batch_id": batch["batch_id"],
        "sample_count": len(sample_entries),
        "samples": sample_entries,
        "metadata": {
            "source_batch_format": batch["format"],
            "write_samples": False,
            "total_event_count": sum(entry["event_count"] for entry in sample_entries),
            "total_graph_edge_count": sum(entry["graph_edge_count"] for entry in sample_entries),
        },
    }


def _sample_index_entry(sample: dict[str, Any], filename: str) -> dict[str, Any]:
    graph = sample["dependency_graph"]
    return {
        "sample_id": sample["sample_id"],
        "filename": filename,
        "label": sample["labels"]["training_target"]["class"],
        "event_count": len(sample["program_events"]),
        "variable_state_count": len(sample["variable_state_sequence"]),
        "graph_node_count": len(graph["nodes"]),
        "graph_edge_count": len(graph["edges"]),
    }


def _validate_batch_shape(batch: dict[str, Any]) -> None:
    if not isinstance(batch, dict):
        raise StaticBatchArtifactError("batch must be an object")
    for field_name in ("format", "batch_id", "samples"):
        if field_name not in batch:
            raise StaticBatchArtifactError(f"missing required batch field: {field_name}")
    if not isinstance(batch["samples"], list):
        raise StaticBatchArtifactError("batch samples must be a list")


def _safe_filename(value: Any) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "_" for character in str(value))
