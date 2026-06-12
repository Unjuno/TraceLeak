#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from traceleak.model_sequence_mlp_comparison import compare_model_sequence_mlp_to_baseline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_path", required=True, type=Path)
    parser.add_argument("--out", dest="output_path", type=Path)
    parser.add_argument("--epochs", default=200, type=int)
    parser.add_argument("--learning-rate", default=0.2, type=float)
    parser.add_argument("--hidden-size", default=8, type=int)
    args = parser.parse_args()
    data = json.loads(args.input_path.read_text(encoding="utf-8"))
    result = compare_model_sequence_mlp_to_baseline(
        data,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        hidden_size=args.hidden_size,
    )
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output_path is None:
        print(encoded)
    else:
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
