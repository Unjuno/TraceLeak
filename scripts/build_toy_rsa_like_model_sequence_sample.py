#!/usr/bin/env python3
"""Build a labeled model-sequence sample from toy RSA-like generated traces.

This connects the toy target generator to the model sequence NN pipeline:

  toy_rsa_like.target.make_run
    -> trace JSONL
    -> extract_model_sequence --counts --label-key
    -> model sequence sample JSON
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from scripts.extract_model_sequence import build_output, extract_model_sequences


class ToyRsaLikeModelSequenceBuildError(ValueError):
    """Raised when toy RSA-like model sequence sample generation fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a toy RSA-like labeled model-sequence sample from generated traces."
    )
    parser.add_argument("--out", dest="output_path", required=True, type=Path, help="Output sample JSON")
    parser.add_argument(
        "--trace-out",
        dest="trace_output_path",
        type=Path,
        help="Optional trace JSONL output path. Defaults to <out>.traces.jsonl",
    )
    parser.add_argument("--runs", type=int, default=16, help="Number of toy runs to generate")
    parser.add_argument(
        "--label-key",
        default="toy_accept_attempt_bucket",
        help="labels_lab_only key to copy into each model-sequence record",
    )
    parser.add_argument(
        "--no-redacted-values",
        action="store_true",
        help="Omit redacted value tokens from model-sequence steps",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload, trace_path = build_toy_rsa_like_model_sequence_sample(
            output_path=args.output_path,
            trace_output_path=args.trace_output_path,
            runs=args.runs,
            label_key=args.label_key,
            include_redacted_values=not args.no_redacted_values,
        )
    except ToyRsaLikeModelSequenceBuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        "wrote toy RSA-like model sequence sample: {sample} ({runs} run(s), trace={trace})".format(
            sample=args.output_path,
            runs=payload["run_count"],
            trace=trace_path,
        )
    )
    return 0


def build_toy_rsa_like_model_sequence_sample(
    *,
    output_path: Path,
    trace_output_path: Path | None = None,
    runs: int = 16,
    label_key: str = "toy_accept_attempt_bucket",
    include_redacted_values: bool = True,
) -> tuple[dict, Path]:
    """Generate toy traces and collapse them into a labeled model-sequence sample."""

    if runs <= 0:
        raise ToyRsaLikeModelSequenceBuildError("--runs must be positive")
    if not label_key:
        raise ToyRsaLikeModelSequenceBuildError("--label-key must not be empty")

    make_run, write_jsonl = _load_toy_target_functions()
    trace_path = trace_output_path or output_path.with_suffix(output_path.suffix + ".traces.jsonl")
    generated_runs = [make_run(index) for index in range(runs)]
    write_jsonl(trace_path, generated_runs)

    records = extract_model_sequences(
        generated_runs,
        allow_raw=False,
        include_counts=True,
        include_redacted_values=include_redacted_values,
        label_key=label_key,
    )
    payload = build_output(
        input_path=trace_path,
        records=records,
        allow_raw=False,
        include_counts=True,
        include_redacted_values=include_redacted_values,
        label_key=label_key,
    )
    payload["target"] = "toy-rsa-like-trace-derived"
    payload["view"] = "redacted"
    payload["notes"] = [
        "Trace-derived toy RSA-like model-sequence sample generated from examples/toy_rsa_like/target.py.",
        "Labels are lab-only buckets copied from labels_lab_only for local evaluation.",
        "This remains a public-safe toy workflow, not real RSA or OpenSSL data.",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload, trace_path


def _load_toy_target_functions() -> tuple[Callable[[int], dict[str, Any]], Callable[[Path, list[dict[str, Any]]], None]]:
    target_path = Path(__file__).resolve().parents[1] / "examples" / "toy_rsa_like" / "target.py"
    spec = importlib.util.spec_from_file_location("traceleak_toy_rsa_like_target", target_path)
    if spec is None or spec.loader is None:
        raise ToyRsaLikeModelSequenceBuildError(f"could not load toy target: {target_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        make_run = module.make_run
        write_jsonl = module.write_jsonl
    except AttributeError as exc:
        raise ToyRsaLikeModelSequenceBuildError(
            f"toy target is missing required function: {exc}"
        ) from exc
    return make_run, write_jsonl


if __name__ == "__main__":
    raise SystemExit(main())
