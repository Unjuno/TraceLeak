"""Lightweight workflow API for TraceLeak.

This module exposes the same public-safe workflow used by scripts/run_experiment.py
as importable Python functions.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from traceleak.attribution import make_ablation_scores
from traceleak.baselines import (
    LabeledFeatureVector,
    label_distribution,
    leave_one_out_majority_accuracy,
    leave_one_out_nearest_neighbor_accuracy,
)
from traceleak.config import load_config, validate_config
from traceleak.features import build_feature_matrix, extract_feature_vector
from traceleak.io import read_jsonl
from traceleak.reporting import attribution_report_dict, write_report_json, write_report_markdown
from traceleak.schema import validate_run


class WorkflowError(ValueError):
    """Raised when a lightweight workflow cannot be completed."""


@dataclass(frozen=True)
class WorkflowResult:
    """Result of a lightweight experiment workflow."""

    experiment_id: str
    written_paths: tuple[Path, ...]


def run_lightweight_experiment(
    config_path: str | Path,
    *,
    out_dir: str | Path = "reports/local",
    root: str | Path | None = None,
) -> WorkflowResult:
    """Run a public-safe lightweight experiment config.

    The workflow performs config validation, trace validation, feature export,
    baseline evaluation, and report generation when the relevant inputs are
    declared in the config.
    """

    root_path = Path.cwd() if root is None else Path(root)
    output_dir = Path(out_dir)
    config = load_config(config_path)
    validate_config(config)

    experiment_id = config["experiment_id"]
    inputs = config.get("inputs", {})
    written: list[Path] = []

    if "trace" in inputs:
        runs = load_public_runs(resolve_path(root_path, inputs["trace"]))
        features_json = configured_output_path(
            config, "features_json", f"{experiment_id}.features.json", output_dir
        )
        features_csv = configured_output_path(
            config, "features_csv", f"{experiment_id}.features.csv", output_dir
        )
        write_features_json(features_json, runs)
        write_features_csv(features_csv, runs)
        written.extend([features_json, features_csv])

    if "baseline" in inputs:
        data, examples = load_baseline_examples(resolve_path(root_path, inputs["baseline"]))
        baseline_json = configured_output_path(
            config, "baseline_json", f"{experiment_id}.baseline.json", output_dir
        )
        write_baseline_result(baseline_json, data, examples)
        written.append(baseline_json)

    if "ablation" in inputs:
        report = load_ablation_report(resolve_path(root_path, inputs["ablation"]))
        report_md = configured_output_path(config, "report_md", f"{experiment_id}.md", output_dir)
        report_json = configured_output_path(config, "report_json", f"{experiment_id}.json", output_dir)
        ensure_parent(report_md)
        ensure_parent(report_json)
        write_report_markdown(report_md, report)
        write_report_json(report_json, report)
        written.extend([report_md, report_json])

    return WorkflowResult(experiment_id=experiment_id, written_paths=tuple(written))


def resolve_path(root: Path, path_text: str) -> Path:
    """Resolve a config path relative to root unless it is already absolute."""

    path = Path(path_text)
    return path if path.is_absolute() else root / path


def configured_output_path(config: dict[str, Any], key: str, default_name: str, out_dir: Path) -> Path:
    """Return configured output path or an out_dir/default_name fallback."""

    configured = config.get("outputs", {}).get(key)
    if configured:
        return Path(configured)
    return out_dir / default_name


def ensure_parent(path: Path) -> None:
    """Create the parent directory for a path."""

    path.parent.mkdir(parents=True, exist_ok=True)


def load_public_runs(path: Path) -> list[dict[str, Any]]:
    """Load JSONL runs and apply public-export validation."""

    runs = list(read_jsonl(path))
    if not runs:
        raise WorkflowError(f"no runs found in {path}")
    for run in runs:
        validate_run(run, public_export=True)
    return runs


def write_features_json(path: Path, runs: list[dict[str, Any]]) -> None:
    """Write feature vectors as JSON."""

    payload = [
        {
            "run_id": run["run_id"],
            "target": run["target"],
            "view": run["view"],
            "features": extract_feature_vector(run),
        }
        for run in runs
    ]
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_features_csv(path: Path, runs: list[dict[str, Any]]) -> None:
    """Write feature vectors as CSV."""

    names, matrix = build_feature_matrix(runs)
    ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run_id", *names])
        for run, row in zip(runs, matrix, strict=True):
            writer.writerow([run["run_id"], *row])


def load_baseline_examples(path: Path) -> tuple[dict[str, Any], list[LabeledFeatureVector]]:
    """Load labeled feature vectors for baseline evaluation."""

    data = json.loads(path.read_text(encoding="utf-8"))
    examples = [
        LabeledFeatureVector(
            label=str(item["label"]),
            features={str(name): float(value) for name, value in item["features"].items()},
            run_id=item.get("run_id"),
        )
        for item in data.get("examples", [])
    ]
    if not examples:
        raise WorkflowError(f"no baseline examples found in {path}")
    return data, examples


def write_baseline_result(path: Path, data: dict[str, Any], examples: list[LabeledFeatureVector]) -> None:
    """Write baseline evaluation result as JSON."""

    result = {
        "target": data.get("target", "unknown"),
        "view": data.get("view", "unknown"),
        "label_name": data.get("label_name", "label"),
        "example_count": len(examples),
        "label_distribution": label_distribution(examples),
        "baselines": {
            "leave_one_out_majority_accuracy": leave_one_out_majority_accuracy(examples),
            "leave_one_out_nearest_neighbor_accuracy": leave_one_out_nearest_neighbor_accuracy(examples),
        },
    }
    ensure_parent(path)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_ablation_report(path: Path) -> dict[str, Any]:
    """Load ablation input and convert it to a report dictionary."""

    data = json.loads(path.read_text(encoding="utf-8"))
    groups = data.get("groups") or {}
    ablated_scores = {
        group_id: float(group_data["ablated_score"])
        for group_id, group_data in groups.items()
    }
    locations = {
        group_id: group_data["location"]
        for group_id, group_data in groups.items()
        if "location" in group_data
    }
    group_types = {group_data.get("group_type", "unknown") for group_data in groups.values()}
    group_type = next(iter(group_types)) if len(group_types) == 1 else "mixed"
    attributions = make_ablation_scores(
        full_score=float(data["full_score"]),
        ablated_scores=ablated_scores,
        group_type=group_type,
        locations=locations,
    )
    return attribution_report_dict(
        target=data["target"],
        view=data["view"],
        metric=data.get("metric", "DeltaH"),
        score=float(data["full_score"]),
        attributions=attributions,
        notes=data.get("notes", []),
    )
