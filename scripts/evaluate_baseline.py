#!/usr/bin/env python3
"""Evaluate lightweight TraceLeak baselines from labeled feature JSON.

Input format:
{
  "target": "synthetic-example",
  "view": "redacted",
  "label_name": "synthetic_bucket",
  "examples": [
    {"run_id": "run_1", "label": "A", "features": {"feature=x": 1.0}}
  ]
}

Usage:
  python scripts/evaluate_baseline.py --in examples/synthetic/baseline_sample.json
  python scripts/evaluate_baseline.py --in examples/synthetic/baseline_sample.json --out baseline_result.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from traceleak.baselines import (
    BaselineError,
    LabeledFeatureVector,
    label_distribution,
    leave_one_out_majority_accuracy,
    leave_one_out_nearest_neighbor_accuracy,
)


class BaselineInputError(ValueError):
    """Raised when baseline CLI input is invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate lightweight TraceLeak baselines.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input labeled feature JSON")
    parser.add_argument("--out", dest="output_path", type=Path, help="Optional JSON output path")
    return parser.parse_args()


def load_input(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise BaselineInputError(f"input file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BaselineInputError(f"invalid JSON in {path}: {exc}") from exc


def parse_examples(data: dict[str, Any]) -> list[LabeledFeatureVector]:
    examples = data.get("examples")
    if not isinstance(examples, list) or not examples:
        raise BaselineInputError("examples must be a non-empty list")

    parsed: list[LabeledFeatureVector] = []
    for index, item in enumerate(examples):
        if not isinstance(item, dict):
            raise BaselineInputError(f"examples[{index}] must be an object")
        if "label" not in item:
            raise BaselineInputError(f"examples[{index}] is missing label")
        if "features" not in item or not isinstance(item["features"], dict):
            raise BaselineInputError(f"examples[{index}] must contain a features object")
        parsed.append(
            LabeledFeatureVector(
                label=str(item["label"]),
                features={str(name): float(value) for name, value in item["features"].items()},
                run_id=item.get("run_id"),
            )
        )
    return parsed


def build_result(data: dict[str, Any]) -> dict[str, Any]:
    examples = parse_examples(data)
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
    return result


def main() -> int:
    args = parse_args()
    try:
        result = build_result(load_input(args.input_path))
    except (BaselineInputError, BaselineError) as exc:
        raise SystemExit(f"error: {exc}") from exc

    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output_path:
        args.output_path.write_text(encoded + "\n", encoding="utf-8")
        print(f"wrote baseline result: {args.output_path}")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
