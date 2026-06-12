#!/usr/bin/env python3
"""Compare model sequence NN training with lightweight baselines.

Usage:
  python scripts/compare_model_sequence_nn_to_baseline.py --in examples/synthetic/model_sequence_nn_hard_sample.json --out comparison.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from traceleak.model_sequence_comparison import (
    ModelSequenceComparisonError,
    compare_model_sequence_nn_to_baseline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare model-sequence NN against baselines.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input model sequence JSON")
    parser.add_argument("--out", dest="output_path", type=Path, help="Optional output JSON path")
    parser.add_argument("--epochs", default=200, type=int, help="Training epochs")
    parser.add_argument("--learning-rate", default=0.8, type=float, help="SGD learning rate")
    parser.add_argument("--l2", default=0.0001, type=float, help="L2 regularization strength")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ModelSequenceComparisonError(f"input file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelSequenceComparisonError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ModelSequenceComparisonError("input must be a JSON object")
    return payload


def main() -> int:
    args = parse_args()
    try:
        result = compare_model_sequence_nn_to_baseline(
            load_json(args.input_path),
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            l2=args.l2,
        )
    except ModelSequenceComparisonError as exc:
        raise SystemExit(f"error: {exc}") from exc

    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output_path is None:
        print(encoded)
        return 0
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(encoded + "\n", encoding="utf-8")
    print(f"wrote model sequence NN comparison: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
