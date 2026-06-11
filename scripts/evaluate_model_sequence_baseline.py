#!/usr/bin/env python3
"""Evaluate lightweight baselines over model sequence token counts.

Usage:
  python scripts/extract_model_sequence.py --in traces.jsonl --out model_sequences.json --counts --label-key secret_bucket
  python scripts/evaluate_model_sequence_baseline.py --in model_sequences.json --out model_sequence_baseline.json
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


class ModelSequenceBaselineError(ValueError):
    """Raised when model sequence baseline input is invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate model sequence token-count baselines.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input model sequence JSON")
    parser.add_argument("--out", dest="output_path", type=Path, help="Optional JSON output path")
    return parser.parse_args()


def load_input(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ModelSequenceBaselineError(f"input file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelSequenceBaselineError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ModelSequenceBaselineError("input must be a JSON object")
    return payload


def parse_labeled_examples(payload: dict[str, Any]) -> list[LabeledFeatureVector]:
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ModelSequenceBaselineError("records must be a non-empty list")

    examples: list[LabeledFeatureVector] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ModelSequenceBaselineError(f"records[{index}] must be an object")
        if "label" not in record:
            raise ModelSequenceBaselineError(
                f"records[{index}] is missing label; rerun extract_model_sequence.py with --label-key"
            )
        counts = record.get("token_counts")
        if not isinstance(counts, dict):
            raise ModelSequenceBaselineError(
                f"records[{index}] is missing token_counts; rerun extract_model_sequence.py with --counts"
            )
        examples.append(
            LabeledFeatureVector(
                label=str(record["label"]),
                features={str(name): float(value) for name, value in counts.items()},
                run_id=record.get("run_id"),
                metadata={
                    "target": record.get("target"),
                    "view": record.get("view"),
                },
            )
        )
    return examples


def build_result(payload: dict[str, Any]) -> dict[str, Any]:
    examples = parse_labeled_examples(payload)
    return {
        "result_type": "model_sequence_baseline",
        "input_format": payload.get("format", "unknown"),
        "target": _common_value(examples, "target"),
        "view": _common_value(examples, "view"),
        "label_name": payload.get("label_name", "label"),
        "example_count": len(examples),
        "label_distribution": label_distribution(examples),
        "baselines": {
            "leave_one_out_majority_accuracy": leave_one_out_majority_accuracy(examples),
            "leave_one_out_nearest_neighbor_accuracy": leave_one_out_nearest_neighbor_accuracy(examples),
        },
        "notes": [
            "Baseline over variable/control-flow model sequence token counts.",
            "This is not neural training; it is a lightweight sanity check before local NN work.",
        ],
    }


def write_or_print(result: dict[str, Any], output_path: Path | None) -> None:
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if output_path is None:
        print(encoded)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(encoded + "\n", encoding="utf-8")
    print(f"wrote model sequence baseline result: {output_path}")


def _common_value(examples: list[LabeledFeatureVector], key: str) -> str:
    values = {str(example.metadata.get(key)) for example in examples if example.metadata and key in example.metadata}
    if len(values) == 1:
        return next(iter(values))
    return "mixed"


def main() -> int:
    args = parse_args()
    try:
        result = build_result(load_input(args.input_path))
    except (BaselineError, ModelSequenceBaselineError) as exc:
        raise SystemExit(f"error: {exc}") from exc
    write_or_print(result, args.output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
