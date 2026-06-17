"""Build module-level static DeepProgramSample batches."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from traceleak.path_manifest_scanner import scan_path_manifest
from traceleak.static_program_sample import build_static_program_deep_sample

STATIC_SAMPLE_BATCH_FORMAT = "traceleak.static_sample_batch.v1"


def build_static_module_sample_batch(
    *,
    root: Path,
    batch_id: str,
    max_paths_per_module: int = 16,
    max_lines_per_file: int = 400,
) -> dict[str, Any]:
    """Build one DeepProgramSample per scanned module group."""

    manifest = scan_path_manifest(root=root, max_paths=4096)
    grouped_paths = _group_paths_by_module([record["path"] for record in manifest["path_records"]])
    samples: list[dict[str, Any]] = []
    sample_summaries: list[dict[str, Any]] = []
    for module_name, paths in sorted(grouped_paths.items()):
        selected_paths = paths[:max_paths_per_module]
        sample = build_static_program_deep_sample(
            root=root,
            relative_paths=selected_paths,
            sample_id=f"{batch_id}:{_module_slug(module_name)}",
            label=f"module:{module_name}",
            max_lines_per_file=max_lines_per_file,
        )
        samples.append(sample)
        sample_summaries.append(_sample_summary(module_name, selected_paths, sample))
    return {
        "format": STATIC_SAMPLE_BATCH_FORMAT,
        "batch_id": batch_id,
        "sample_count": len(samples),
        "samples": samples,
        "metadata": {
            "root_name": manifest["root_name"],
            "content_read_enabled": True,
            "module_count": len(grouped_paths),
            "max_paths_per_module": max_paths_per_module,
            "sample_summaries": sample_summaries,
            "total_event_count": sum(summary["event_count"] for summary in sample_summaries),
            "total_graph_edge_count": sum(summary["graph_edge_count"] for summary in sample_summaries),
        },
    }


def _sample_summary(module_name: str, paths: list[str], sample: dict[str, Any]) -> dict[str, Any]:
    graph = sample["dependency_graph"]
    return {
        "sample_id": sample["sample_id"],
        "module": module_name,
        "path_count": len(paths),
        "event_count": len(sample["program_events"]),
        "variable_state_count": len(sample["variable_state_sequence"]),
        "graph_node_count": len(graph["nodes"]),
        "graph_edge_count": len(graph["edges"]),
    }


def _group_paths_by_module(paths: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for path in paths:
        module_name = _module_from_path(path)
        grouped.setdefault(module_name, []).append(path)
    return grouped


def _module_from_path(path: str) -> str:
    parts = [part for part in path.replace("\\", "/").split("/") if part]
    if not parts:
        return "unknown"
    if parts[0] == "crypto" and len(parts) >= 2:
        return f"crypto/{parts[1]}"
    if parts[0] == "ssl" and len(parts) >= 2:
        return f"ssl/{parts[1]}"
    return parts[0]


def _module_slug(module_name: str) -> str:
    return module_name.replace("/", "_").replace("-", "_")
