#!/usr/bin/env python3
"""Train a minimal neural model over TraceLeak model sequence token counts.

Usage:
  python scripts/train_model_sequence_nn.py --in examples/synthetic/model_sequence_baseline_sample.json --out model_result.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from traceleak.model_sequence_nn import ModelSequenceNNError, train_model_sequence_nn_result
from traceleak.model_results import ModelResultError, validate_model_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a minimal model-sequence neural classifier.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input model sequence JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output model result JSON")
    parser.add_argument(
        "--experiment-id",
        default="exp_model_sequence_nn_local",
        help="Experiment id to write into the model result",
    )
    parser.add_argument("--epochs", default=200, type=int, help="Training epochs")
    parser.add_argument("--learning-rate", default=0.8, type=float, help="SGD learning rate")
    parser.add_argument("--l2", default=0.0001, type=float, help="L2 regularization strength")
    parser.add_argument(
        "--top-k-attributions",
        default=8,
        type=int,
        help="Maximum number of token attributions to include",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ModelSequenceNNError(f"input file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelSequenceNNError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ModelSequenceNNError("input must be a JSON object")
    return payload


def main() -> int:
    args = parse_args()
    try:
        result = train_model_sequence_nn_result(
            load_json(args.input_path),
            experiment_id=args.experiment_id,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            l2=args.l2,
            top_k_attributions=args.top_k_attributions,
        )
        validate_model_result(result)
    except (ModelSequenceNNError, ModelResultError) as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote model sequence neural result: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
