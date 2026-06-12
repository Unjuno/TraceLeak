#!/usr/bin/env python3
"""Run ablation checks for a model-sequence sample."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.model_sequence_audit import (
    ModelSequenceAuditError,
    ablation_report_markdown,
    load_model_sequence_sample,
    model_sequence_ablation_report,
    write_json,
    write_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run model-sequence ablation checks.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path, help="Input sample JSON")
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output report path")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--epochs", type=int, default=80, help="Sparse softmax training epochs")
    parser.add_argument("--learning-rate", type=float, default=0.8, help="Sparse softmax learning rate")
    parser.add_argument("--l2", type=float, default=0.0001, help="L2 regularization strength")
    parser.add_argument("--top-drop-k", type=int, default=2, help="Number of top attribution tokens to drop")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = load_model_sequence_sample(args.input_path)
        report = model_sequence_ablation_report(
            data,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            l2=args.l2,
            top_drop_k=args.top_drop_k,
        )
    except ModelSequenceAuditError as exc:
        raise SystemExit(f"error: {exc}") from exc

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        write_json(args.output_path, report)
    else:
        write_markdown(args.output_path, ablation_report_markdown(report))
    print(f"wrote model sequence ablation report: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
