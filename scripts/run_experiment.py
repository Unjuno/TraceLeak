#!/usr/bin/env python3
"""Run a lightweight TraceLeak experiment config.

This runner performs only repository-safe lightweight steps:

1. validate the experiment config
2. validate the configured trace file
3. export features when a trace input is present
4. evaluate baselines when a baseline input is present
5. generate reports when an ablation input is present

Usage:
  python scripts/run_experiment.py experiments/exp_000_synthetic_leak/config.json
  python scripts/run_experiment.py experiments/exp_000_synthetic_leak/config.json --out-dir reports/local
"""

from __future__ import annotations

import argparse
import csv
import json
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a lightweight TraceLeak experiment config.")
    parser.add_argument("config", type=Path, help="Experiment config JSON")
    parser.add_argument("--out-dir", type=Path, default=Path("reports/local"), help="Output directory")
    return parser.parse_args()


def resolve_path(root: Path, path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else root / path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_runs(path: Path) -> list[dict[str, Any]]:
    runs = list(read_jsonl(path))
    if not runs:
        raise ValueError(f"no runs found in {path}")
    for run in runs:
        validate_run(run, public_export=True)
    return runs


def write_features_json(path: Path, runs: list[dict[str, Any]]) -> None:
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
    names, matrix = build_feature_matrix(runs)
    ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run_id", *names])
        for run, row in zip(runs, matrix, strict=True):
            writer.writerow([run["run_id"], *row])


def load_baseline_examples(path: Path) -> tuple[dict[str, Any], list[LabeledFeatureVector]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    examples = []
    for item in data.get("examples", []):
        examples.append(
            LabeledFeatureVector(
                label=str(item["label"]),
                features={str(name): float(value) for name, value in item["features"].items()},
                run_id=item.get("run_id"),
            )
        )
    if not examples:
        raise ValueError(f"no baseline examples found in {path}")
    return data, examples


def write_baseline_result(path: Path, data: dict[str, Any], examples: list[LabeledFeatureVector]) -> None:
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


def output_path(config: dict[str, Any], key: str, default_name: str, out_dir: Path) -> Path:
    configured = config.get("outputs", {}).get(key)
    if configured:
        return Path(configured)
    return out_dir / default_name


def main() -> int:
    args = parse_args()
    root = Path.cwd()
    config = load_config(args.config)
    validate_config(config)

    experiment_id = config["experiment_id"]
    inputs = config.get("inputs", {})
    written: list[Path] = []

    if "trace" in inputs:
        runs = load_runs(resolve_path(root, inputs["trace"]))
        features_json = output_path(config, "features_json", f"{experiment_id}.features.json", args.out_dir)
        features_csv = output_path(config, "features_csv", f"{experiment_id}.features.csv", args.out_dir)
        write_features_json(features_json, runs)
        write_features_csv(features_csv, runs)
        written.extend([features_json, features_csv])

    if "baseline" in inputs:
        data, examples = load_baseline_examples(resolve_path(root, inputs["baseline"]))
        baseline_json = output_path(config, "baseline_json", f"{experiment_id}.baseline.json", args.out_dir)
        write_baseline_result(baseline_json, data, examples)
        written.append(baseline_json)

    if "ablation" in inputs:
        report = load_ablation_report(resolve_path(root, inputs["ablation"]))
        report_md = output_path(config, "report_md", f"{experiment_id}.md", args.out_dir)
        report_json = output_path(config, "report_json", f"{experiment_id}.json", args.out_dir)
        ensure_parent(report_md)
        ensure_parent(report_json)
        write_report_markdown(report_md, report)
        write_report_json(report_json, report)
        written.extend([report_md, report_json])

    for path in written:
        print(f"wrote: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
